#!/bin/sh
# import_backup.sh
pg_restore -U postgres -v -d bazaDanych /docker-entrypoint-initdb.d/backup.dump
