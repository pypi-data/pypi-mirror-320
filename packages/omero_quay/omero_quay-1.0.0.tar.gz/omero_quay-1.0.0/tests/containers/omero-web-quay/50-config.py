#!/usr/bin/env python
# 1. Run .omero files from /opt/omero/web/config/
# 2. Set omero config properties from CONFIG_ envvars
#    Variable names should replace "." with "_" and "_" with "__"
#    E.g. CONFIG_omero_web_public_enabled=false

import os
from subprocess import run
from re import sub


OMERO = "/opt/omero/web/venv3/bin/omero"


completed_process = run(
    [OMERO, "load", "--glob", "/opt/omero/web/config/*.omero"], capture_output=True
)
completed_process.check_returncode()

for (k, value) in os.environ.items():
    if k.startswith("CONFIG_"):
        prop = k[7:]
        prop = sub("([^_])_([^_])", r"\1.\2", prop)
        prop = sub("__", "_", prop)
        completed_process = run(
            [OMERO, "config", "set", "--", prop, value], capture_output=True
        )
        completed_process.check_returncode()
