#!/usr/bin/env bash

set -o pipefail

ENDPOINT=()

function join { local IFS="$1"; shift; echo -n "$*"; }

if [ -z $PORT ]
then
    PORT=9092
fi

if [ -z $SINCEDB ]
then
    echo '$SINCEDB missing'
    exit 1
fi

if [ -z $JDS ]
then
    echo '$JDS missing'
    exit 1
fi

if [ -z $ETCD_DIR ]
then
    echo '$ETCD_DIR missing'
    exit 1
fi

i=0
while true
do
    IP=$(curl -s localhost:2379/v2/keys/${ETCD_DIR} | \
        jq -e -r .node.nodes[$i].value)
    if [ $? -ne 0 ]
    then
        echo "$i out of range in ${ETCD_DIR}"
        break
    fi
    ENDPOINT+=("$IP:$PORT")
    let i++
done

exec $JDS $(join , ${ENDPOINT[@]}) $SINCEDB