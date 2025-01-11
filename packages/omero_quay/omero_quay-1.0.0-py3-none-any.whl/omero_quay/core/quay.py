"""
from https://github.com/zeromq/pyzmq/blob/main/examples/eventloop/asyncweb.py
"""

from __future__ import annotations

import logging
import threading

import zmq
from tornado import web
from zmq.eventloop.future import Context as FutureContext

from .core.workers import (
    get_proxy,
    get_respond_worker,
    get_transfer_worker,
    get_watcher_worker,
)
from .managers.irods import iRODSManager
from .managers.omero import OmeroManager
from .watchers.omero import OmeroWatcher

log = logging.getLogger(__name__)

"""
As a general rule use bind from the most stable points in your
architecture, and use connect from dynamic components with volatile
endpoints. For request/reply, the service provider might be the point
where you bind and the clients are using connect. Just like plain old
TCP.
"""


class Handler(web.RequestHandler):
    """
        curl -X POST -H "Content-Type: application/json" \
           -d '{"investigation": "group1", "study": "study0"}' \
           http://localhost:8888
    """

    async def get(self) -> None:
        self.write("This server is only intended for POST requests")

    async def post(self) -> None:
        ctx = FutureContext.instance()
        s = ctx.socket(zmq.DEALER)

        s.connect("tcp://127.0.0.1:5553")

        if msg := self.request.body:
            await s.send(msg)
        else:
            await s.send(b"hello from post")

        # wait for worker's reply
        reply = await s.recv_string()
        log.info("\nfinishing with %r\n", reply)
        self.write(reply)
        return reply


async def setup(conf) -> None:
    respond_worker = get_respond_worker(5553, 5554)
    responder = threading.Thread(target=respond_worker)
    responder.daemon = True
    responder.start()
    log.info("Started first worker")

    proxy = get_proxy(5554, 5555)
    proxythread = threading.Thread(target=proxy)
    proxythread.daemon = True
    proxythread.start()
    log.info("Started proxy")

    omero_watcher = get_watcher_worker(
        OmeroWatcher,
        send_port=5554,
        conf=conf["omero"],
    )
    omewatch = threading.Thread(target=omero_watcher)
    omewatch.daemon = True
    omewatch.start()
    log.info("Started omero watcher")

    irods_transfer = get_transfer_worker(
        iRODSManager,
        receive_port=5555,
        send_port=5556,
        conf=conf["irods"],
        dry=False,
    )
    mover = threading.Thread(target=irods_transfer)
    mover.daemon = True
    mover.start()
    log.info("Started irods worker")

    omero_transfer = get_transfer_worker(
        OmeroManager,
        receive_port=5556,
        send_port=5557,
        conf=conf["omero"],
        dry=False,
    )
    importer = threading.Thread(target=omero_transfer)
    importer.daemon = True
    importer.start()
    log.info("Started omero worker")
    application = web.Application([(r"/", Handler)])
    application.listen(8888)
