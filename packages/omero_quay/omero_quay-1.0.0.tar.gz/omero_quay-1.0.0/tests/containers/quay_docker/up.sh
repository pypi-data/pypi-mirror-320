#!/bin/bash

# build latest image
docker build -t gitlab-registry.in2p3.fr/fbi-data/omero-quay/quay-docker .

# Run irods_import.py
docker run --rm -it --name quay --network=containers_omero \
        --mount type=bind,source="$(pwd)"/quay.yml,target=/tmp/omero-quay/quay.yml \
        --mount type=bind,source="$(pwd)"/omero-server,target=/tmp/omero-quay/omero-server \
        gitlab-registry.in2p3.fr/fbi-data/omero-quay/quay-docker python scripts/irods_import.py
