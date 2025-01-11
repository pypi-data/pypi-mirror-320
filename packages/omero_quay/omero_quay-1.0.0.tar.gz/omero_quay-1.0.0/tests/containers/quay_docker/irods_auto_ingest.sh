#!/bin/bash

export CELERY_BROKER_URL="redis://127.0.0.1:6379/0"
export PYTHONPATH=`pwd`

redis-server --bind 127.0.0.1 --port 6379 --daemonize yes
celery -A irods_capability_automated_ingest.sync_task worker -l warning -Q restart,path,file -c 20 -D
exec "$@"
