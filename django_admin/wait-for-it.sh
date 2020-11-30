#!/bin/bash

host="db"
port="5432"

>&2 echo "Checking database for availability"

until pg_isready -d movies -h db -p 5432 -U django; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 1
done

>&2 echo "Database is up"
