from __future__ import annotations

import json
import warnings
from itertools import product
from pathlib import Path
from typing import TYPE_CHECKING

from linkml_runtime.loaders import yaml_loader

from ..core.manifest import Manifest, User
from . import OmeroUser, SambaUser, iRODSUser

if TYPE_CHECKING:
    pass

class_mapping = {
    "irods": iRODSUser,
    "samba": SambaUser,
    "omero": OmeroUser,
}


def _get_classes(schemes):
    try:
        return [class_mapping[scheme] for scheme in schemes]
    except KeyError as err:
        unknown = set(schemes).difference(class_mapping)
        msg = f"schemes {unknown} are not supported"
        raise ValueError(msg) from err


#
def from_users_json(
    users_json: str | Path, schemes: list[str], mapping: dict | None = None
):
    """available schemes:
    irods, ldap, samba, omero
    """

    with Path(users_json).open("r", encoding="utf-8") as fh:
        users = json.load(fh)
    classes = _get_classes(schemes)
    for kls, user in product(classes, users):
        _kls = kls.from_dict(user, mapping=mapping)
        _kls.crud()


def from_manifest(manifest: Manifest | str | Path, schemes: list[str]):
    """available schemes:
    irods, ldap, samba, omero
    """
    if not isinstance(manifest, Manifest):
        with Path(manifest).open("r") as fh:
            manifest = yaml_loader.load(fh, target_class=Manifest)
    users = {}
    for investigation in manifest.investigations:
        users.update({user.name: user for user in investigation.members})
    crud(users.values(), schemes)


def crud(users: list[User] | str, schemes: list[str]):
    classes = _get_classes(schemes)
    for kls, user in product(classes, users):
        kls(user).crud()


def create(users_json, irods=True, samba=False):
    warnings.warn("Deprecated, use `crud` instead", stacklevel=1)
    classes = []
    if samba:
        classes.append(SambaUser)
    if irods:
        classes.append(iRODSUser)

    for kls, user in product(classes, users_json):
        kls(user).crud()
