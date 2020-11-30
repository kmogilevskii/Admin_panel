#!/bin/bash

until curl -s django:8000 > /dev/null; do
  >&2 echo "Django is unavailable - sleeping"
  sleep 1
done

>&2 echo "Django is up"

exit 0
