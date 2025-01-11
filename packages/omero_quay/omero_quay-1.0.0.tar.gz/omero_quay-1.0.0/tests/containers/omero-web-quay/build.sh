#!/bin/bash

set -e
set -u

export PREFIX=${TRAVIS_BRANCH:-test}
export HOST=${HOST:-localhost}

if [ -n "${DOCKER_USERNAME:-}" -a -z "${REPO:-}" ]; then
    REPO="${DOCKER_USERNAME}"
else
    REPO="${REPO:-test}"
fi
IMAGE=$REPO/omero-web:$PREFIX
STANDALONE=$REPO/omero-web-standalone:$PREFIX

CLEAN=${CLEAN:-y}

cleanup() {
    docker rm -f -v $PREFIX-web
}

if [ "$CLEAN" = y ]; then
    trap cleanup ERR EXIT
fi

cleanup || true

make VERSION="$PREFIX" REPO="$REPO" docker-build

docker run -d --name $PREFIX-web \
    -e CONFIG_omero_web_server__list='[["omero.example.org", 4064, "test-omero"]]' \
    -e CONFIG_omero_web_debug=true \
    -p 4080:4080 \
    --network=host \
    $IMAGE

/bin/sh test_getweb.sh

# Standalone image
cleanup
docker run -d --name $PREFIX-web \
    -e CONFIG_omero_web_server__list='[["omero.example.org", 4064, "test-omero"]]' \
    -e CONFIG_omero_web_debug=true \
    -p 4080:4080 \
    --network=host \
    $STANDALONE

bash test_getweb.sh
