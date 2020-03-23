#!/bin/sh

set -e

case $1 in
    conexample)
        alembic -c /migrations/alembic.ini upgrade head
        exec uwsgi --yaml uwsgi.yml
        exit $?
        ;;
esac

exec "$@"
