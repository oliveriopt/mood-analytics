#!/usr/bin/env bash

export PATH=/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH="${PYTHONPATH}:/app"

cd engage-analytics


python3 sentiment_analysis/src/extract_from_db_insert_weeks_to_redis.py --company_id="e9464795-d6e0-11e7-9246-42010a840018"
