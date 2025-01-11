"""Connection helpers to LDAP, iRODS, OMERO and madbot"""

from __future__ import annotations

import logging

log = logging.getLogger()

log = logging.getLogger()


try:
    from irods.session import iRODSSession
except ImportError:
    log.info(
        """iRODS python client is not installed, if you need it you can install it with
        pip install python-irodsclient"""
    )
try:
    from ldap3 import ALL, Connection, Server
except ImportError:
    log.info(
        "ldap3 module not available, install it with pip install ldap3 if you need it"
    )

try:
    import ezomero
    from omero.cli import CLI
except ImportError:
    log.info("Can't use Omero connection, run pip install omero-quay[server]")

try:
    from fabric import Connection as SSHConnection
except ImportError:
    log.info("Can't use ssh connection, run pip install omero-quay[ssh]")


class OmeroSSHCLI:
    """Instance of a OMERO SSH command line interface"""

    def __init__(self, conf, *opts, user=None):
        self.conf = conf
        remote_user = conf["omero"]["OMEROSERVER_USER"]
        remote_host = conf["omero"]["OMEROSERVER_HOST"]
        remote_port = conf["omero"].get("OMEROSERVER_PORT", 22)
        self.conn = SSHConnection(f"{remote_user}@{remote_host}:{remote_port}")
        self.user = user
        self.opts = opts

    def invoke(self, args):
        admin = self.conf["omero"]["OMERO_ADMIN"]
        password = self.conf["omero"]["OMERO_ADMIN_PASS"]
        host = self.conf["omero"]["OMERO_HOST"]
        port = self.conf["omero"]["OMERO_PORT"]
        login = (
            f"omero login -w {password} --sudo {admin} {' '.join(self.opts)} "
            f"{self.user}@{host}:{port}"
        )
        if self.user:
            self.conn.run(login)
        else:
            self.conn.run(f"omero login -w {password} {admin}@{host}:{port}")

        command = " ".join(args)
        self.conn.run(f"omero {command}")


def omero_conn(conf):
    """returns a BlitzGateway connection object

    Args:
        conf (json?): output of get_conf() function.
    """

    # https://github.com/ome/omero-cli-transfer/blob/baeb5094430820bf8b0baa499a8faee70e026b09/.omero/wait-on-login
    secure = conf["omero"]["OMERO_HOST"] != "localhost"

    conn = ezomero.connect(
        user=conf["omero"]["OMERO_ADMIN"],
        password=conf["omero"]["OMERO_ADMIN_PASS"],
        host=conf["omero"]["OMERO_HOST"],
        port=conf["omero"]["OMERO_PORT"],
        group=conf["omero"].get("OMERO_GROUP", ""),
        secure=secure,
    )
    conn.SERVICE_OPTS.setOmeroGroup(-1)
    conn.c.enableKeepAlive(5)
    return conn


def omero_sudo_conn(conf, username, group=None):
    """returns a BlitzGateway connection object. For sysadmins.

    Args:
        conf (json?): output of get_conf() function.
    """

    # https://github.com/ome/omero-cli-transfer/blob/baeb5094430820bf8b0baa499a8faee70e026b09/.omero/wait-on-login
    secure = conf["omero"]["OMERO_HOST"] != "localhost"

    conn = ezomero.connect(
        user=conf["omero"]["OMERO_ADMIN"],
        password=conf["omero"]["OMERO_ADMIN_PASS"],
        host=conf["omero"]["OMERO_HOST"],
        port=conf["omero"]["OMERO_PORT"],
        group=conf["omero"].get("OMERO_GROUP", ""),
        secure=secure,
    )
    conn.SERVICE_OPTS.setOmeroGroup(-1)
    conn.c.enableKeepAlive(5)
    return conn.suConn(username, group)


def omero_sudo_cli(conf, user, opts=None):
    """Returns an omero CLI instance and connects it
    as the user with the sudo option

    Args:
        conf (json?): output of get_conf() function.
    """
    if opts is None:
        opts = []

    admin = conf["omero"]["OMERO_ADMIN"]
    password = conf["omero"]["OMERO_ADMIN_PASS"]
    host = conf["omero"]["OMERO_HOST"]
    port = conf["omero"]["OMERO_PORT"]
    cli = CLI()
    # FIXME use session key?
    cli.loadplugins()
    log.info("sudo login as %s", user)
    args = ["login", "-w", password, "--sudo", admin, *opts, f"{user}@{host}:{port}"]
    cli.invoke(args, strict=True)
    return cli


def omero_admin_cli(conf, opts=None):
    """Returns an omero admin CLI instance

    Args:
        conf (yaml file): output of get_conf() function.
    """

    if opts is None:
        opts = []
    admin = conf["omero"]["OMERO_ADMIN"]
    password = conf["omero"]["OMERO_ADMIN_PASS"]
    host = conf["omero"]["OMERO_HOST"]
    port = conf["omero"]["OMERO_PORT"]
    password = conf["omero"]["OMERO_ADMIN_PASS"]
    cli = CLI()
    # cli.conn().SERVICE_OPTS.setOmeroGroup(-1)
    args = ["login", "-w", password, *opts, f"{admin}@{host}:{port}"]
    # FIXME use session key?
    cli.loadplugins()

    cli.invoke(args)
    return cli


def omero_ssh_cli(conf, user=None):
    return OmeroSSHCLI(conf, user)


def irods_conn(conf):
    """Returns an iRODSSession instance"""
    return iRODSSession(
        host=conf["irods"]["IRODS_HOST"],
        port=conf["irods"]["IRODS_PORT"],
        user=conf["irods"]["IRODS_ADMIN_USER"],
        zone=conf["irods"]["IRODS_ZONE"],
        password=conf["irods"]["IRODS_ADMIN_PASS"],
    )


def irods_sudo_conn(conf, username):
    """Returns an iRODSSession instance"""
    return iRODSSession(
        host=conf["irods"]["IRODS_HOST"],
        port=conf["irods"]["IRODS_PORT"],
        user=conf["irods"]["IRODS_ADMIN_USER"],
        zone=conf["irods"]["IRODS_ZONE"],
        password=conf["irods"]["IRODS_ADMIN_PASS"],
        client_user=username,
    )


def ldap_conn(conf):
    """Returns an ldap3 Connection instance"""
    host = conf["ldap"]["LDAP_HOST"]
    port = conf["ldap"]["LDAP_PORT"]
    admin = conf["ldap"]["LDAP_ADMIN_USER"]
    admin_passwd = conf["ldap"]["LDAP_ADMIN_PASS"]
    server = Server(host, port, get_info=ALL)

    return Connection(server, admin, admin_passwd, auto_bind=True, read_only=False)
