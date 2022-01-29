#!/usr/bin/env bash
set -u
set -o pipefail

# Function to execute SQL statement
execDBStatement() {
  PGPASSWORD=$WRITE_DB_PASS psql \
  --username=$WRITE_DB_USER \
  --dbname=postgres \
  --host=$WRITE_DB_HOST \
  --command="$1"
}

# If this is the test runner...
if [[ -v UNIT_TEST ]]; then
    execDBStatement "CREATE DATABASE ${DB_NAME}_test;"
else
  # Create Postgres Database
  execDBStatement "CREATE DATABASE ${DB_NAME};"
fi
