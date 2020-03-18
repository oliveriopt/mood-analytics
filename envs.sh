#!/usr/bin/env bash

export APP_ENV=dev
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=root
export API_DB_NAME=mood_prod_mirror
export INSIGHTS_DB_NAME=mood_insights_develop
export SLACK_TOKEN=xpto
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=5
export GOOGLE_STORAGE_KEY_PATH=${PWD}/keys/mood-2364f0d6fc3e.json
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_STORAGE_KEY_PATH}
export GOOGLE_STORAGE_BUCKET=mood-reports