from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from irods_capability_automated_ingest.core import Core
from irods_capability_automated_ingest.utils import Operation

from omero_quay.clients.excel import excel_request

log = logging.getLogger("transfer_queue")
log.setLevel("INFO")
handler_file = Path.cwd() / "transfer_queue.txt"
handler = logging.FileHandler(handler_file.as_posix())
formatter = logging.Formatter("%(asctime)s;%(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)
strhandler = logging.StreamHandler()
log.addHandler(strhandler)


class event_handler(Core):
    """This subclass defines specific actions at ingest"""

    @staticmethod
    def post_data_obj_create(hdlr_mod, logger, session, meta, **options):  # noqa:ARG004
        # TODO: see if we assume the excel file is only written once
        logical_path = meta.get("path", "")
        if logical_path.endswith("import.xlsx"):
            asyncio.run(excel_request(logical_path))

    @staticmethod
    def as_user(meta, **options):  # noqa:ARG004
        log_path = meta.get("target", "")
        user = log_path.split("/")[3]
        return "devZone", user

    @staticmethod
    def operation(session, meta, **options):  # noqa:ARG004
        return Operation.PUT_SYNC
