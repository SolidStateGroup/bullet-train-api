#!/bin/bash
set -e

function migrate () {
    python manage.py migrate && python manage.py createcachetable
}
function serve() {
    export STATSD_PORT=${STATSD_PORT:-8125}
    export STATSD_PREFIX=${STATSD_PREFIX:-flagsmith.api}

    gunicorn --bind 0.0.0.0:8000 \
             --worker-tmp-dir /dev/shm \
             --timeout ${GUNICORN_TIMEOUT:-30} \
             --workers ${GUNICORN_WORKERS:-3} \
             --threads ${GUNICORN_THREADS:-2} \
             --access-logfile $ACCESS_LOG_LOCATION \
             --keep-alive ${GUNICORN_KEEP_ALIVE:-2} \
             ${STATSD_HOST:+--statsd-host $STATSD_HOST:$STATSD_PORT} \
             ${STATSD_HOST:+--statsd-prefix $STATSD_PREFIX} \
             app.wsgi
}
function migrate_identities(){
    python manage.py migrate_to_edge "$1"
}
function import_organisation_from_s3(){
    python manage.py importorganisationfroms3 "$1" "$2"
}
function dump_organisation_to_s3(){
    python manage.py dumporganisationtos3 "$1" "$2" "$3"
}
function dump_organisation_to_local_fs(){
    python manage.py dumporganisationtolocalfs "$1" "$2"
}

if [ "$1" == "migrate" ]; then
    migrate
elif [ "$1" == "serve" ]; then
    serve
elif [ "$1" == "migrate_identities" ]; then
    migrate_identities "$2"
elif [ "$1" == "import-organisation-from-s3" ]; then
    import_organisation_from_s3 "$2" "$3"
elif [ "$1" == "dump-organisation-to-s3" ]; then
    dump_organisation_to_s3 "$2" "$3" "$4"
elif [ "$1" == "dump-organisation-to-local-fs" ]; then
    dump_organisation_to_local_fs "$2" "$3"
elif [ "$1" == "migrate-and-serve" ]; then
    migrate
    serve
else
   echo "ERROR: unrecognised command '$1'"
fi
