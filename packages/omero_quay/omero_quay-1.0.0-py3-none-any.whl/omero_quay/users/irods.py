from __future__ import annotations

from irods.exception import UserDoesNotExist

from ..core.config import get_conf
from ..core.connect import irods_conn
from .crud_user import CRUDUser

mapping = {}


class iRODSUser(CRUDUser):
    def exists(self):
        conf = get_conf()
        with irods_conn(conf) as sess:
            try:
                return sess.users.get(self.user.name)
            except UserDoesNotExist:
                return False

    def delete(self):
        conf = get_conf()
        with irods_conn(conf) as sess:
            sess.users.remove(self.user.name)

    def create(self):
        conf = get_conf()
        with irods_conn(conf) as sess:
            sess.users.create(self.user.name, "rodsuser", user_zone=conf["irods"]["IRODS_ZONE"])

    def update(self):
        conf = get_conf()
        with irods_conn(conf) as sess:
            sess.users.get(self.user.name)
