#! /bin/bash -e

setup_input_file=/tmp/server_config.json

if [ -e "${setup_input_file}" ]; then
    echo "Running iRODS setup"
    python3 /var/lib/irods/scripts/setup_irods.py -v --json_configuration_file "${setup_input_file}"
fi

echo "Starting server"

cd /usr/sbin
su irods -c 'bash -c "./irodsServer -u"'
