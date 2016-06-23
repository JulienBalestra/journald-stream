#!/usr/bin/env bash

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

for i in $(etcdctl ls /$ETCD_DIR)
do
    IP=$(etcdctl get $i)
    ENDPOINT+=("$IP:$PORT")
done

exec $JDS $(join , ${ENDPOINT[@]}) $SINCEDB