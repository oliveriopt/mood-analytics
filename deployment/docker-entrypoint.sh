#!/usr/bin/env bash

printenv | sed 's/^\(.*\)$/export \1/g' > /root/.env

exec "$@"