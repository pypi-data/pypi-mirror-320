from __future__ import annotations

import asyncio
import json
import logging

import zmq
import zmq.asyncio
from linkml_runtime.dumpers import json_dumper
from linkml_runtime.loaders import json_loader
from pydantic import ValidationError
from zmq.asyncio import Context

from ..managers.filesystem import FSManager
from ..managers.irods import iRODSManager
from ..managers.omero import OmeroManager
from ..mdp.client import Client
from ..mdp.scheduler import Scheduler
from ..mdp.worker import Worker
from ..watchers.omero import OmeroWatcher
from .manifest import Manifest

NUM_DISPATCH = 10  # Number of possible parallel imports
NUM_WORKERS = 10


log = logging.getLogger(__name__)


workers_map = {
    "watchers": {"omero": OmeroWatcher},
    "managers": {
        "omero": OmeroManager,
        "irods": iRODSManager,
        "file": FSManager,
    },
}


def init_event_loop():
    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)
    return loop


async def dispatch():
    ctx = Context.instance()
    router = ctx.socket(zmq.ROUTER)
    router.setsockopt(zmq.IDENTITY, b"dispatch")
    router.bind(f"tcp://*:{5556}")

    message = await router.recv_multipart()
    *_, manifest_json = message
    manifest_json = manifest_json.decode("utf-8")
    log.info("Entering dispatch with %s", manifest_json[:10])

    counter = 0
    while counter < 10_000:
        try:
            manifest = json_loader.loads(manifest_json, target_class=Manifest)
        except (json.JSONDecodeError, ValidationError):
            log.error(
                "Validation Error for request with message %s",
                json.dumps(manifest_json, sort_keys=True, indent=4),
            )
            return None
        service = choose_service(manifest)
        if service is None:
            log.info("No target service found for manifest %s", manifest.id)
            log.info("Waiting for a new message")
            message = await router.recv_multipart()
            *_, manifest_json = message
            manifest_json = manifest_json.decode("utf-8")
            continue

        log.info(
            "Dispatch task %d: treating manifest %s with states: %s",
            counter,
            manifest.id,
            manifest.states,
        )
        client = Client()
        manifest_json = json_dumper.dumps(manifest)
        log.info("dispatch is about to submit")
        await client.submit(service, [bytes(manifest_json, "utf-8")])
        log.info("Submitted manifest to service %s", service)
        reply_service, msg = await client.get()
        log.info("Got reply %s from service %s", msg[0][:10], reply_service)
        manifest_json = msg[-1].decode("utf-8")
        client.disconnect()
        counter += 1

    return manifest_json


def choose_service(manifest: Manifest) -> str | None:
    for state in manifest.states:
        service = bytes(f"{state.scheme}_{state.host}", encoding="utf-8")  # _{idx:03d}
        log.info("identity %s, state %s", service, state)
        match state.status:
            case "errored":
                log.info("state for service %s is errored, aborting", service)
                return None
            case "started" | "expired":
                return service
            case "changed":
                state.status = "checked"
                continue
            case "checked":
                continue

    return None


async def brocker(stop_event):
    scheduler = Scheduler(stop_event)
    await scheduler.on_recv_message()


async def manager_worker(stop_event, manager_class, conf, service, dry=False):
    """TODO"""

    async def run_manager(*message):
        log.info("Manager got message")
        manifest_json = message[0].decode("utf-8")
        manifest = json_loader.loads(manifest_json, target_class=Manifest)
        log.info("%s got manifest %s", manager_class.__name__, manifest.id)

        with manager_class(conf=conf, manifest=manifest) as mngr:
            log.info(
                "%s manager instantiated, with state %s",
                manager_class.__name__,
                mngr.state,
            )
            match mngr.state.status:
                case "started" | "expired":
                    log.info("There's work to do")
                    try:
                        manifest_json = _manage(mngr, dry=dry)
                        log.info("%s manager managed managely", mngr.scheme)
                    except Exception as e:
                        log.error("Manager errored", exc_info=e)
                        mngr.set_state("errored")
                        manifest_json = json_dumper.dumps(mngr.manifest)
                        return [bytes(manifest_json, "utf-8")]

                case "errored":
                    msg = "Should not visit that state"
                    raise RuntimeError(msg)
                case "changed":
                    mngr.set_state("checked")
                    manifest_json = json_dumper.dumps(mngr.manifest)

        return [bytes(manifest_json, "utf-8")]

    worker = Worker(stop_event)
    await worker.run(service, run_manager)


def _manage(mngr, dry=False):
    log.info("Started to treat manager")
    mngr.parse(parse_links=True)
    if not dry:
        log.info("started crud")
        mngr.crud()
        log.info("finished crud")
        mngr.transfer()
        log.info("finished transfer")
        log.info("Parse again")
        mngr.parse(parse_links=False)
        mngr.crud()
        mngr.cleanup()
        log.info("finished cleanup")
        mngr.set_state("changed")
        for state in mngr.manifest.states:
            if (state.host == mngr.host) and (state.scheme == mngr.scheme):
                continue
            if state.status in ("checked", "changed"):
                continue
            state.status = "expired"

    if mngr.manifest.error is not None:
        log.error(
            "Got an error in manifest %s: %s",
            mngr.manifest.id,
            mngr.manifest.error,
        )
        mngr.set_state("errored")
    return json_dumper.dumps(mngr.manifest)


async def watcher_worker(watcher_class, conf):
    with watcher_class(conf) as watcher:
        log.info("waiting for watcher %s", watcher_class.__name__)
        async for manifest in watcher.watch():
            log.info("Got manifest from watcher")
            manifest_json = json_dumper.dumps(manifest)
            service = choose_service(manifest)
            client = Client()
            log.info(
                "watcher %s is about to submit to %s", watcher_class.__name__, service
            )
            await client.submit(service, [bytes(manifest_json, "utf-8")])
            log.info("Submitted manifest to service %s", service)
            reply_service, msg = await client.get()
            log.info("Got reply %s from service %s", msg[0][:10], reply_service)


"""


workers_map = {
    # "watchers": {"omero": OmeroWatcher},
    "managers": {
        "omero": OmeroManager,
        "irods": iRODSManager,
        "file": FSManager,
    },
}
"""


async def setup(conf: dict) -> None:
    log.info("Collecting coroutines")
    stop_event = asyncio.Event()
    coroutines = [brocker(stop_event)]

    for _ in range(NUM_DISPATCH):
        coroutines.append(dispatch())

    if packers := conf.get("workers").get("packers"):
        for packer_conf in packers.values():
            scheme = packer_conf["scheme"]
            manager_class = workers_map["managers"][scheme]
            host = packer_conf["host"]
            service = bytes(f"{scheme}_{host}", "utf-8")
            log.info("Registered %s manager coroutines", packer_conf["scheme"])
            coroutines.append(
                manager_worker(stop_event, manager_class, conf, service, dry=True)
            )
    if watchers := conf.get("workers").get("watchers"):
        for watcher_conf in watchers.values():
            scheme = watcher_conf["scheme"]
            watcher_class = workers_map["watchers"][scheme]
            log.info("Registering %s watcher coroutines", scheme)
            coroutines.append(watcher_worker(watcher_class, conf))

    if managers := conf.get("workers").get("managers"):
        for manager_conf in managers.values():
            scheme = manager_conf["scheme"]
            manager_class = workers_map["managers"][scheme]
            host = manager_conf["host"]
            service = bytes(f"{scheme}_{host}", "utf-8")
            log.info("Registered %s manager coroutines", manager_conf["scheme"])
            for _ in range(NUM_WORKERS):
                coroutines.append(
                    manager_worker(stop_event, manager_class, conf, service)
                )

    await asyncio.gather(*coroutines, return_exceptions=True)
