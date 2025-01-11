#!/bin/bash

docker compose restart omero-server
docker exec -u root omero-server mount -t nfs -o \
  "rw,intr,soft,noatime,tcp,timeo=14,nolock,nfsvers=4" \
  nfsrods:/home /mnt/SHARE

