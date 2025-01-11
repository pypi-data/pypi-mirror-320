from __future__ import annotations

import argparse

from irods.access import iRODSAccess

from omero_quay.core.config import get_conf
from omero_quay.core.connect import irods_sudo_conn
from omero_quay.users.authentik import get_users
from omero_quay.users.manage import crud


def get_args():
    parser = argparse.ArgumentParser(
        prog="atk2smb",
        description="""Command line interface to create users the facility SAMBA from authentik.

                    The environment variable AUTHENTIK_TOKEN should be set with a valid token
                    """,
    )
    parser.add_argument(
        "instance",
        help="Instance from which we select users, e.g. Nantes or Montpellier",
    )  # positional argument
    parser.add_argument(
        "facility",
        help="Facility on which this is running, e.g. irs or mri",
    )  # positional argument
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    users = get_users(args.instance)
    crud(users, ["irods"])
    conf = get_conf()
    for user in users:
        with irods_sudo_conn(conf, user.name) as sess:
            facility_coll = (
                f"/{conf['irods']['IRODS_ZONE']}/home/{user.name}/{args.facility}"
            )
            if not sess.collections.exists(facility_coll):
                sess.collections.create(facility_coll)

            inh_acl = iRODSAccess("inherit", facility_coll)
            sess.acls.set(inh_acl)
            acl = iRODSAccess("own", facility_coll, user.name, user_type="rodsuser")
            sess.acls.set(acl)
            acl = iRODSAccess(
                "own",
                facility_coll,
                conf["irods"]["IRODS_ADMIN_USER"],
                user_type="rodsuser",
            )
            sess.acls.set(acl)

    for user in users:
        user.name = user.name.replace("@", ".").lower()
    crud(users, ["samba"])
