#!/bin/bash
set -eE
trap if_fail ERR

cat << "EOF"
 ____    ____    ______          __            __
/\  _`\ /\  _`\ /\__  _\        /\ \          /\ \__
\ \ \L\_\ \ \L\ \/_/\ \/        \_\ \     __  \ \ ,_\    __
 \ \  _\/\ \  _ <' \ \ \        /'_` \  /'__`\ \ \ \/  /'__`\
  \ \ \/  \ \ \L\ \ \_\ \__  __/\ \L\ \/\ \L\.\_\ \ \_/\ \L\.\_
   \ \_\   \ \____/ /\_____\/\_\ \___,_\ \__/.\_\\ \__\ \__/.\_\
    \/_/    \/___/  \/_____/\/_/\/__,_ /\/__/\/_/ \/__/\/__/\/_/

EOF

for arg in "$@"; do
  shift
  case "$arg" in
    '--web')    set -- "$@" '-w'   ;;
    '--down')   set -- "$@" '-d'   ;;
    '--purge')  set -- "$@" '-p'   ;;
    *)          set -- "$@" "$arg" ;;
  esac
done

up_omeroweb=false
url="https://zenodo.org/records/13353626/files/data.tar.gz?download=1"

OPTIND=1
while getopts ':wdp' OPTION; do
  case "$OPTION" in
    'w')
      up_omeroweb=true
      ;;
    'd')
      docker compose down
      exit
      ;;
    'p')
      docker compose down -v
      exit
      ;;
    '?')
      echo "script usage: $(basename "$0") [-w --web]" >&2
      exit 1
      ;;
  esac
done
# shellcheck disable=SC2004
shift "$(($OPTIND -1))"

if [ -z "${QUAY_TEST_DATA}" ]; then
  export QUAY_TEST_DATA="./QuayTestData"
  echo "QUAY_TEST_DATA not set, defaulting to $QUAY_TEST_DATA"
fi

if [ -z "${CI_COMMIT_BRANCH}" ]; then
  export CI_COMMIT_BRANCH="dev"
  echo "CI_COMMIT_BRANCH not set, defaulting to $CI_COMMIT_BRANCH"
fi

function if_fail () {
  echo "Script failed, killing all container and exiting"
  docker compose down -v
}

function check_dir () {
  for dir do
    if [[ ! -d $dir  ]]; then
      mkdir -p "$dir"
      chmod -R 766 "$dir"
    else
      echo "$dir already exist"
      chmod -R 766 "$dir"
    fi
  done
}

function healthcheck () {
  docker inspect --format='{{json .State.Health.Status}}' "$1"
}

# Check if needed dir exists
check_dir "$QUAY_TEST_DATA"/data

if [[ -z $(ls -A "$QUAY_TEST_DATA"/data) ]]; then
  curl -o /tmp/data.tar.gz "$url" \
    && tar -xvzf /tmp/data.tar.gz -C /tmp/
  mv /tmp/data/* "$QUAY_TEST_DATA"/data
fi
chmod -R 777 "$QUAY_TEST_DATA"

# standup irods
docker compose pull --quiet irods-icat
docker compose pull --quiet irods-db
docker compose up -d --no-build irods-icat

# Wait for irods container before creating users
# sleep 5 for CI
echo "Waiting until iRods server is healthy..."
until healthcheck irods-icat = "healthy"; do sleep 1; done
echo "iRods server started"

until
  docker exec -u irods irods-icat iadmin lu;
do
  echo "Retrying..."
  sleep 10;
done

sleep 10

if docker exec -u irods irods-icat iadmin lu | grep omero-server; then
  echo "iRods user omero-server already exist..."
  docker exec -u irods irods-icat iadmin moduser omero-server password omero-root-password;
else
  echo "Creating iRods user omero-server..."
  until
    docker exec -u irods irods-icat iadmin mkuser omero-server rodsadmin;
  do
    echo "Retrying...";
  done
  docker exec -u irods irods-icat iadmin moduser omero-server password omero-root-password
fi

# standup nfsrods
docker compose up -d --no-build nfsrods

# standup omero
docker compose up -d --no-build  omero-server

echo "Waiting until Omero server is healthy..."
sleep 10
until healthcheck omero-server = "healthy"; do sleep 1; done
echo "Omero server started"

sleep 10


echo "Mount NFSrods volume on omero-server"
docker exec -u root omero-server mount -t nfs -o \
  "rw,intr,soft,noatime,tcp,timeo=14,nolock,nfsvers=4" \
  nfsrods:/home /mnt/SHARE

docker compose up -d mongo

if $up_omeroweb; then
  docker compose up -d omero-web
fi

until
  docker exec -u omero-server omero-server /opt/omero/server/OMERO.server/bin/omero user list -s localhost -u root -w omero
do
  sleep 3
done

echo "Omero server started"

if up_omeroweb=true; then
  docker compose up -d omero-web
fi
