from __future__ import annotations

import logging
import os

from pathlib import Path

from linkml_runtime.loaders import yaml_loader

from omero_quay.core.manifest import Manifest
from omero_quay.users.manage import from_manifest
from omero_quay.core.config import get_conf

log = logging.getLogger("omero_quay")
log.setLevel("DEBUG")

conf = get_conf()
DATA_PATH = conf["pytest"]["DOCKER_DATA_PATH"]

manifest = yaml_loader.load(
    f"{DATA_PATH}/users/test_users.yml", target_class=Manifest
)
from_manifest(manifest, schemes=["omero", "irods"])
