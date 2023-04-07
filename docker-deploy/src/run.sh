#!/bin/sh
# run.sh
set -e
host="db:5432"
shift
cmd="python3 server.py >/dev/null"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "postgres" -c '\q'; do
  sleep 1
done

exec $cmd