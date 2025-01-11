from __future__ import annotations

import logging

from omero.rtypes import rstring

from ..core.config import get_conf
from ..core.connect import omero_admin_cli, omero_conn
from .crud_user import CRUDUser

log = logging.getLogger(__name__)

mapping: dict = {
    "user_name": "name",
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email",
    "institution": "institution",
}


class OmeroUser(CRUDUser):
    def exists(self):
        conf = get_conf()
        with omero_conn(conf) as conn:
            users = conn.getObjects(
                "Experimenter",
                attributes={"omeName": self.user.name},
            )
            try:
                return next(iter(users))
            except StopIteration:
                return False

    def delete(self):
        conf = get_conf()
        cli = omero_admin_cli(conf)
        log.info("Deactivating user %s in omero", self.user.name)
        cli.invoke(
            [
                "user",
                "leavegroup",
                "user",
                f"--name={self.user.name}",
            ]
        )

    def create(self):
        conf = get_conf()
        cli = omero_admin_cli(conf)
        cli.invoke(
            [
                "group",
                "add",
                "default",
            ]
        )

        if self.user.email:
            cli.invoke(
                [
                    "user",
                    "add",
                    "-P",
                    "omero",
                    "-e",
                    self.user.email,
                    self.user.name,
                    self.user.first_name,
                    self.user.last_name,
                    "default",
                ]
            )
        else:
            cli.invoke(
                [
                    "user",
                    "add",
                    "-P",
                    "omero",
                    self.user.name,
                    self.user.first_name,
                    self.user.last_name,
                    "default",
                ]
            )

    def update(self):
        conf = get_conf()
        with omero_conn(conf) as conn:
            conn.SERVICE_OPTS.setOmeroGroup(0)
            conn.getUpdateService()
            users = conn.getObjects(
                "Experimenter",
                attributes={"omeName": "user0"},
            )
            ome_user = next(iter(users))
            ome_user.setFirstName(rstring(self.user.first_name))
            ome_user.setLastName(rstring(self.user.last_name))
            if self.user.email:
                ome_user.setEmail(rstring(self.user.email))
            ome_user.save()
