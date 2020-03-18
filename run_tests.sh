#!/usr/bin/env bash

export PATH=/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH="${PYTHONPATH}:/app"

redis-server &

TEST_STATUS=0
pytest --cov=. --cov-report=html --cov-report=xml
TEST_STATUS=$?

if [[ ${APP_ENV} == "deploy" ]]; then
    # Move /app/reports and /app/test_coverage to one single folder called /test_coverage
    cp -R /app/htmlcov/. /tests_coverage
    mkdir -p /tests_coverage/reports
    cp /app/coverage.xml /tests_coverage/reports
fi

exit ${TEST_STATUS}
