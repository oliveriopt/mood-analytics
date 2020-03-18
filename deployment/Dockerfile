FROM python:latest

ENV APP_ENV staging
ENV DB_HOST 127.0.0.1
ENV DB_USER root
ENV DB_PASSWORD secret
ENV DB_PORT 3306
ENV API_DB_NAME mood-develop
ENV INSIGHTS_DB_NAME mood-develop
ENV SLACK_TOKEN token
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV TZ=UTC \
  DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV DISPLAY=:10
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y \
  python3-tk \
  curl \
  redis-server \
  default-jdk


COPY . /app

RUN chmod +x /app/run_tests.sh

RUN python3 -m venv /venv
RUN pip3 install -q --no-cache-dir -r requirements.txt

ENV STACKDRIVER_AGENT_URL="https://raw.githubusercontent.com/kununu/stackdriver-mysql-custom-metrics-agent/master"
RUN pip3 install -q --no-cache-dir -r "${STACKDRIVER_AGENT_URL}/requirements.txt" \
  && curl -fsSLO "${STACKDRIVER_AGENT_URL}/agent.py" && chmod +x agent.py

# due to based google-cloud-api version installed by stackdriver requirements is not supported by the sentiment analysis pipeline
RUN pip3 install --upgrade google-cloud-storage

