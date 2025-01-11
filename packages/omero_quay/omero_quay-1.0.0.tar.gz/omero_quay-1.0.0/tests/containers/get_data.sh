#!/bin/bash
set -e

url="https://zenodo.org/records/13353626/files/data.tar.gz?download=1"


quay_test_data=${QUAY_TEST_DATA:=$HOME/QuayTestData}
export QUAY_TEST_DATA=$quay_test_data

mkdir -p "$quay_test_data"
echo "$quay_test_data"


wget -O /tmp/data.tar.gz --show-progress "$url" \
    && tar -xvzf /tmp/data.tar.gz -C /tmp/
mv /tmp/data "$quay_test_data"/data
