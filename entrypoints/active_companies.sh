#!/usr/bin/env bash

export PATH=/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH="${PYTHONPATH}:/app"

cd /app/engage-analytics

NEW_RELIC_CONFIG_FILE=/etc/newrelic.ini newrelic-admin run-program python3 active_companies.py

