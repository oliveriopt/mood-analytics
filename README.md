# mood-analytics

This repository features analytics tools for engage needs.
It holds a pipeline containing several units for distinct validations.

# Pipeline validations

1. Active companies


# How to run

Project can be run with docker, via CLI or IDE.
In all of them ENV vars need to be set accordingly:

## ENV vars

```
APP_ENV=<env>
DB_HOST=<host>
DB_PORT=<port>
DB_USER=<user>
DB_PASSWORD=<pw>
API_DB_NAME=<api-db>
INSIGHTS_DB_NAME=<insights-db>
SLACK_TOKEN=<slack-token>
```

**IMPORTANT:**

`APP_ENV` ["prod","release","develop","dev"] may not be set. If so it will use "dev" mode.

This project must have access to API and INSIGHTS database. It assumes they are both on the same server and credentials provided can be used to access both.


## Instructions

Docker
___

**cwd: active-companies**
```
docker build -t analytics .
docker run --env-file .envs analytics
```

**.envs** is the file containing all the ENV vars and that are injected during container start.

CLI
___
**cwd: active-companies**
```
source envs.sh
PYTHONPATH=. python3 main.py
```

IDE
___
1. Load ENV vars into the environment vars settings on the configurations
2. Execute intended program
