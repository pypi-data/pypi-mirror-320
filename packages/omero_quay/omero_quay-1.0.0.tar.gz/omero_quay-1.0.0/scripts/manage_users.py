from __future__ import annotations

import argparse

from omero_quay.users import LdapUser, SambaUser, iRODSUser
from omero_quay.users.manage import from_users_json

# TODO : pass this in the configuration
json_mapping = {
    "name": "uid",
    "password": "userPassword",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "unix_uid": "uidNumber",
    "unix_gid": "uidNumber",
}


def get_args():
    parser = argparse.ArgumentParser(
        prog="quay-user",
        description="Command line interface to create users in iRODS-OMERO",
    )
    parser.add_argument("json_path")  # positional argument
    parser.add_argument(
        "-l",
        "--ldap",
        action="store_true",
        help="Create the user in ldap",
    )

    parser.add_argument(
        "-i",
        "--irods",
        action="store_true",
        help="Create the user in irods",
    )

    parser.add_argument(
        "-s",
        "--samba",
        action="store_true",
        help="Create the user in samba",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    print(args)  # noqa:T201

    classes = []
    if args.ldap:
        classes.append(LdapUser)
    if args.samba:
        classes.append(SambaUser)
    if args.irods:
        classes.append(iRODSUser)

    resp = from_users_json(args.json_path, classes, mapping=json_mapping)
    print(resp)  # noqa:T201
