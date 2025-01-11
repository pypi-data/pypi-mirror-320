#!/bin/bash
set -e


conda activate quay && python create_users.py
docker exec -u irods icat iadmin moduser facility0 password omero
