"""

"""

from __future__ import annotations

import argparse
import logging

import requests
from linkml_runtime.dumpers import json_dumper

from omero_quay.parsers.filesystem import gen_manifest

log = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(
        prog="omero_quay_cli",
        description="Command line interface to import data in iRODS-OMERO",
    )
    parser.add_argument("path")  # positional argument
    parser.add_argument(
        "-i",
        "--investigation",
        required=True,
        help="The investigation to import in",
    )
    parser.add_argument(
        "-s",
        "--study",
        help="The study to import in",
    )
    parser.add_argument(
        "-a",
        "--assay",
        help="The assay to import in",
    )
    parser.add_argument(
        "-u",
        "--user",
        help="The user owning the data",
        required=True,
    )

    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-H", "--host", default="localhost")
    parser.add_argument("-P", "--port", default="8888")

    return parser.parse_args()


def import_client(args):
    if args.assay:
        depth = 0
        hierarchy = {
            "investigation": args.investigation,
            "study": args.study,
            "assay": args.assay,
        }
    elif args.study:
        depth = 1
        hierarchy = {
            "investigation": args.investigation,
            "study": args.study,
        }

    elif args.investigation:
        depth = 2
        hierarchy = {
            "investigation": args.investigation,
        }
    if any(v is None for v in hierarchy.values()):
        msg = f"Incomplete hierarchy {hierarchy}"
        raise ValueError(msg)

    manifest = gen_manifest(
        args.path,
        depth=depth,
        hierarchy=hierarchy,
        owner_name=args.user,
    )
    manifest_json = json_dumper.dumps(manifest)
    return requests.post(
        f"http://{args.host}:{args.port}", data=manifest_json, timeout=3000
    )


if __name__ == "__main__":
    args = get_args()
    print(args)  # noqa:T201
    resp = import_client(args)
    print(resp)  # noqa:T201
