#!/bin/bash
#
# Submit all workloads in the ./workloads directory.
#
# The COSBENCH_PATH environment variable must be defined
# and point to the root of the cosbench directory.
#

WORKLOAD_DIR="./workloads/"

if [ -z "$COSBENCH_PATH" ]; then
    echo "COSBENCH_PATH is not defined"
    exit 1
fi

for workload in $(ls $WORKLOAD_DIR); do
    # Generate a unique HASH value so that objects aren't overwritten
    # between runs if purge hasn't completed.
    hash=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)

    # The hash is unique for each run so we will cp to /tmp
    cp $WORKLOAD_DIR/$workload /tmp/$workload
    sed -i "s/_HASH_/$hash/g" /tmp/$workload
    $COSBENCH_PATH/cli.sh submit /tmp/$workload
done
