from __future__ import annotations

import asyncio
import json
import logging

import zmq
import zmq.asyncio
from linkml_runtime.loaders import json_loader
from motor import motor_tornado
from pydantic import ValidationError
from tornado import web
from zmq.asyncio import Context

from ..core.config import get_conf
from .manifest import Manifest

log = logging.getLogger(__name__)


def parse_mongo_query(request):
    req_args = {
        k: [u.decode("utf-8").replace("'", '"') for u in v]
        for k, v in request.query_arguments.items()
    }
    kwargs = {}
    if query := req_args.get("query"):
        kwargs["filter"] = json.loads(query[0])
    if limit := req_args.get("limit"):
        kwargs["limit"] = int(limit[0])
    if projection := req_args.get("projection"):
        kwargs["projection"] = projection
    if sort := req_args.get("sort"):
        field, order = sort
        kwargs["sort"] = [(field, int(order))]
    else:
        # Sort by descending creation date by default
        kwargs["sort"] = [("creation_date", -1)]
    return kwargs


class Handler(web.RequestHandler):
    """
        curl -X POST -H "Content-Type: application/json" \
           -d '{"investigation": "group1", "study": "study0"}' \
           http://localhost:8888
    """

    async def get(self) -> None:
        db = self.settings["db"]
        kwargs = parse_mongo_query(self.request)
        log.debug("Got request with parameters: %s", kwargs)
        cursor = db.manifests.find(**kwargs)
        documents = await cursor.to_list(length=30)
        log.debug("found %d manifests", len(documents))
        self.write(json.dumps(documents))

    async def post(self) -> None:
        log.info("Handler got a post message")
        if msg := self.request.body:
            log.info("handler got message %s from 8888", msg[:100])
            try:
                manifest_json = msg.decode("utf-8")
                _ = json_loader.loads(manifest_json, target_class=Manifest)
            except (json.JSONDecodeError, ValidationError):
                log.error("Validation Error in http handler for  message %s", msg)
                self.write("400")
                return
            await self._send(manifest_json)
            self.write(manifest_json)
            log.info("Exiting http handler post method")

    async def _send(self, manifest_json):
        context = Context.instance()

        with context.socket(zmq.REQ) as sender:
            identity = bytes("dispatch", "utf-8")
            sender.setsockopt(zmq.IDENTITY, identity)
            sender.connect(f"tcp://localhost:{5556}")
            await sender.send_string(manifest_json)
            #  Don't wait for the reply
            # await sender.recv_string()
            # log.info("handler got reply from %d", out_port)


async def tornado_server():
    conf = get_conf()
    if "mongo" in conf:
        client = motor_tornado.MotorClient(
            conf["mongo"]["DB_URL"], conf["mongo"]["DB_PORT"]
        )
        db = client.quay
    else:
        db = None
    application = web.Application([(r"/", Handler)], db=db)
    application.listen(8888)
    await asyncio.Event().wait()


def tornado_server_process():
    asyncio.run(tornado_server())
