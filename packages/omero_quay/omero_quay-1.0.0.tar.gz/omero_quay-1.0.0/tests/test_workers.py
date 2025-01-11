""" """

from __future__ import annotations

import asyncio

import pytest

from omero_quay.clients.excel import excel_request
from omero_quay.core.config import get_conf


@pytest.mark.skip(reason="Wait for docker to do this properly")
def test_fs_service(fs_service, request_client, fs_manifest):
    asyncio.gather(fs_service(), request_client(fs_manifest), return_exceptions=True)


@pytest.mark.skip(reason="Wait for docker to do this properly")
def test_excel_import(xlsx_import_path):
    asyncio.run(excel_request(xlsx_import_path, conf=get_conf()))
