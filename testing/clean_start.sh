#!/bin/bash

# This script is intended to ensure that the SQLite database
# file has been removed and recreated with migrations applied.
# Then it will start up the actual Django testing/dev server.

rm -f /app/db.sqlite3

cd /app

python manage.py migrate

if [ $? -ne 0 ]; then
  echo -e "\n ** Error applying migrations to DB file!! **\n"
  exit 1
fi

python manage.py runserver 0.0.0.0:8000