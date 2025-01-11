from __future__ import annotations

import json
from pathlib import Path

from linkml_runtime.loaders import yaml_loader

from omero_quay.core.manifest import Manifest
from omero_quay.users import OmeroUser
from omero_quay.users.crud_user import CRUDUser
from omero_quay.users.manage import from_manifest

json_mapping = {
    "name": "uid",
    "password": "userPassword",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "unix_uid": "uidNumber",
    "unix_gid": "uidNumber",
}


def test_from_json(test_users_json):
    with Path(test_users_json).open("r", encoding="utf-8") as fh:
        users = json.load(fh)

    manager = CRUDUser.from_json(json.dumps(users[0]), json_mapping=json_mapping)
    assert manager.user.name


def test_from_manifest(users_manifest):
    with Path(users_manifest).open("r") as fh:
        manifest = yaml_loader.load(fh, target_class=Manifest)
    from_manifest(users_manifest, schemes=["omero", "irods"])

    user = manifest.investigations[0].members[0]
    ome_user = OmeroUser(user).exists()
    assert ome_user
    user.first_name = "Newname"
    from_manifest(manifest, schemes=["omero", "irods"])
    # ome_user = OmeroUser(user).exists()
    # assert ome_user.getFirstName() == "Newname"
