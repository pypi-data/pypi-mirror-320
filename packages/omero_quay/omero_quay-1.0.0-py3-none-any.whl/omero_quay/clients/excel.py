from __future__ import annotations

import logging
import os
import json
from datetime import datetime

import httpx
from linkml_runtime.dumpers import json_dumper, yaml_dumper

from omero_quay.core.config import get_conf
from omero_quay.core.manifest import State
from omero_quay.parsers.excel import parse_xlsx

log = logging.getLogger(__name__)


async def excel_request(xlsx, conf=None):
    """Send a POST request with Excel XLSX content converted to JSON, to iRODS.
    returns nothing.
    """
    if conf is None:
        conf = get_conf()
    post_url = conf["ingest"]["POST_URL"]
    timeout = conf["ingest"]["timeout"]
    try:
        manifest = parse_xlsx(xlsx)
    except Exception as e:
        log.info("Error parsing excel file %s", xlsx)
        raise e
    for worker in conf["workers"]["managers"].values():
        now = datetime.now().isoformat()
        state = State(
            scheme=worker["scheme"],
            host=worker["host"],
            timestamp=now,
            status="started",
        )
        manifest.states.append(state)
    manifest_json = json_dumper.dumps(manifest)
    log.info("Sending manifest : %s from excel", manifest.id)
    log.info("Manifest content :\n %s", yaml_dumper.dumps(manifest))
    http_proxy = os.environ.get("HTTP_PROXY", None)
    async with httpx.AsyncClient(proxy=http_proxy) as client:
        resp = await client.post(post_url, data=manifest_json, timeout=timeout)
        log.info("Got response: %s", resp)
    manifest = json.loads(resp.text)
    return manifest["id"]
