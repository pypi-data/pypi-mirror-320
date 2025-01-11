#!/usr/bin/env python
#
# Copyright (c) 2024 FBI.data.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

import httpx
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from omeroweb.decorators import login_required

from omero_quay.clients.excel import excel_request
from omero_quay.core.config import get_conf
from omero_quay.core.manifest import Manifest
from omero_quay.parsers import validate_excel
from omero_quay.parsers.errors import ExcelValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


BASE_DIR = Path(__file__).parent.resolve()
# unix only
HOME = Path(os.environ["HOME"])


syslog_handler = logging.handlers.SysLogHandler()
syslog_handler.setLevel("DEBUG")
logger.addHandler(syslog_handler)


# /tmp/omero_import_webui_files/log_files
quay_path = HOME / "quay-import"
log_path = quay_path / "logs"

log_path.mkdir(parents=True, exist_ok=True)

filelog_handler = logging.FileHandler(log_path / "main.log")
filelog_handler.setLevel("DEBUG")
logger.addHandler(filelog_handler)

# os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger.info("WebImportUI module imported")

users_files_path = quay_path / "user_excel_files"
users_files_path.mkdir(parents=True, exist_ok=True)

log_files_path = log_path


def import_to_meso(xlsx_file):
    """
    Send a XLSX file to mesocenter, to be processed by omero-quay on mesocenter

    Args:
        xlsx_file: XLSX metadata file. Must be valid.
    """
    config_data = get_conf()
    asyncio.run(excel_request(xlsx_file, config_data))


# login_required: if not logged-in, will redirect to webclient
# login page. Then back to here, passing in the 'conn' connection
# and other arguments **kwargs.
@login_required()
def index(request, conn=None, **kwargs):
    """
    Main Django app function. Returns a Django request.

    Args:
        request: Django request. Mandatory.
        conn: OMERO connection. See OMERO doc for that.
    """
    logger.info("Logging works!")
    # We can load data from OMERO via Blitz Gateway connection.
    # See https://docs.openmicroscopy.org/latest/omero/developers/Python.html
    # A dictionary of data to pass to the html template
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
        "request_get_parameters": str(request.GET),
        "request_post_parameters": str(request.POST),
        "list_of_files": [],
        "list_of_files_states": [],
        "last_state_string": "En attente",
        "job_states": [],
        "error_messages": [],
        "jobs": ["xlsx", "irods", "omero"],
        "manifests": [],
        "timestamp": datetime.today(),
    }

    context.update(kwargs)
    user_directory_name = "{firstName}_{lastName}_{experimenterId}".format(**context)
    user_path = quay_path / user_directory_name
    user_path.mkdir(parents=True, exist_ok=True)

    config_data = get_conf()

    http_proxy = os.environ.get("HTTP_PROXY", None)
    logger.info("Proxy: %s", http_proxy)
    with httpx.Client(proxy=http_proxy) as client:
        req = client.get(
            config_data["ingest"]["POST_URL"],
            params={
                "limit": 5,
                "projection": [
                    "investigations",
                    "states",
                    "creation_date",
                    "error",
                    "manager",
                ],
            },
        )
        logger.info("Got %d answers", len(req.json()))

    for m in req.json():
        m["id"] = m.pop("_id")
        manifest = Manifest(**m)
        logger.info("Loaded manifest %s", m["id"])
        context["manifests"].append(m)
        if manifest.error is not None:
            context["error_messages"].append(manifest.error.message)

    logger.info("MANIFESTS: %s", context["manifests"])
    ################
    fs = FileSystemStorage(location=user_path.as_posix())

    if "send_button" in request.POST and request.method == "POST":
        logger.info("RAW_REQUEST: %s", list(request))
        logger.info("POST_REQUEST: %s", list(request.POST.items()))

        if myfile := request.FILES["myfile"]:
            filename = fs.save(myfile.name, myfile)
            context["last_state_string"] = f"File: {filename} loaded "
        else:
            context["last_state_string"] = "No file"
        context["list_of_files"] = [p.name for p in user_path.iterdir()]
        return render(request, "quay_import/index.html", context)

    if "delete_button" in request.POST and request.method == "POST":
        logger.info("POST_REQUEST: %s", list(request.POST.items()))

        dict_items = dict(request.POST.items())
        for filename, associated_value in dict_items.items():
            if associated_value == "on":
                fs.delete(filename)
                state_string = f"{filename}: Effacé"
                context["list_of_files_states"].append(state_string)
        context["last_state_string"] = "Fichiers sélectionnés effacés"
        context["list_of_files"] = [p.name for p in user_path.iterdir()]
        return render(request, "quay_import/index.html", context)

    if "send_files_to_mesocenter" in request.POST and request.method == "POST":
        logger.info("POST_REQUEST: %s", list(request.POST.items()))

        dict_items = dict(request.POST.items())
        for filename, associated_value in dict_items.items():
            if associated_value == "on":
                item_path = user_path / filename
                logger.info("ITEM_PATH: %s", item_path)
                config_data = get_conf()
                logger.debug("CONFIG DATA from omero-quay: %s", config_data)
                try:
                    validate_excel.check_everything(item_path)
                    asyncio.run(excel_request(item_path, config_data))
                    fs.delete(filename)
                    state_string = f"{filename}: Envoyé"
                    context["list_of_files_states"].append(state_string)
                    logger.info(state_string)
                    context[
                        "last_state_string"
                    ] = "Fichiers sélectionnés envoyés vers mésocentre"
                except ExcelValidationError as e:
                    state_string = f"{filename}: Erreur: {e}"
                    context["list_of_files_states"].append(state_string)
                    logger.info(state_string)
                context["list_of_files"] = [p.name for p in user_path.iterdir()]
        return render(request, "quay_import/index.html", context)

    return render(request, "quay_import/index.html", context)
