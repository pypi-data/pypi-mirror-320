from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from fabric import Connection
from paramiko.ssh_exception import SSHException

from ..core.config import get_conf
from .crud_user import CRUDUser

conf = get_conf()
users_home = conf["ingest"]["MOUNT_PATH"]

# samba-tool cli arguments
# see `samba-tool user add -h`
mapping: dict = {
    "given-name": "first_name",
    "surname": "last_name",
    "mail-address": "email",
    "uid-number": "unix_uid",
    "gid-number": "unix_gid",
}

log = logging.getLogger(__name__)


class SambaUser(CRUDUser):
    # TODO: see about uidNumber and gidNumber (if they are required)

    def exists(self):
        cmd = ["samba-tool", "user", "show", self.user.name]
        try:
            results = _remote_run(cmd, conf["smb"]["ADDC_HOSTS"])
            # subprocess.run(["sudo", *cmd], check=True)
        except Exception:
            return False

        for res in results:
            if hasattr(res, "return_code") and res.return_code != 0:
                return False
            if hasattr(res, "returncode") and res.returncode != 0:
                return False

        cmd = [
            "sudo",
            "samba-tool",
            "user",
            "show",
            "--attributes=mail",
            self.user.name,
        ]

        res = subprocess.run(
            cmd,
            capture_output=True,
            check=False,
        )
        try:
            mail = res.stdout.decode("utf-8").split("\n")[1].split(":")[1].strip()
        except IndexError:
            return True

        if mail == self.user.email:
            return True

        original_name = self.user.name
        if original_name[-1].isnumeric():
            num = int(original_name[-1]) + 1
            self.user.name = f"{self.user.name[:-1]}{num}"
        else:
            self.user.name = f"{self.user.name}1"

        return False

    def delete(self):
        cmd = ["samba-tool", "user", "delete", self.user.name]
        _remote_run(cmd, conf["smb"]["ADDC_HOSTS"])

    def create(self):
        newuser = {k: self.user.dict()[v] for k, v in mapping.items()}
        newuser["home-directory"] = f"/home/{self.user.name}"

        args = [f"--{k}={v}" for k, v in newuser.items()]
        # sudo samba-tool domain passwordsettings set --complexity=off --min-pwd-length=3 --min-pwd-age=0
        cmd = [
            "samba-tool",
            "user",
            "add",
            self.user.name,
            self.user.name,  # use username as default password
            "--must-change-at-next-login",
            "--use-username-as-cn",
            *args,
        ]

        try:
            _remote_run(cmd, conf["smb"]["ADDC_HOSTS"])
        except Exception as e:
            log.error("Error at user %s creation", self.user.name, exc_info=e)
            return

    def update(self):
        log.info("Nothing done, with for python client implementation")
        # self.delete()
        # self.create()


#  TODO error management
def _remote_run(cmd, hosts):
    results = []
    for host in hosts:
        if host in ("localhost", "127.0.0.1"):
            completed = subprocess.run(["sudo", *cmd], check=True)
            results.append(completed)
            # TODO get the output
        else:
            conn = Connection(host)
            try:
                results.append(conn.sudo(" ".join(cmd)))
            except SSHException:
                log.error("Connection error for server %s", conn.host)
    return results
