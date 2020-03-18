#!/usr/bin/env bash

if [ -z ${PHRASEAPP_PROJECT_ID} ]; then
    echo "Env var <PHRASEAPP_PROJECT_ID> must be set"
    exit 1
elif [ -z ${PHRASEAPP_ACCESS_TOKEN} ]; then
    echo "Env var <PHRASEAPP_ACCESS_TOKEN> must be set"
    exit 1
fi

APP_DIR=${PWD}
PHRASE_APP_CONFIG=".phraseapp.yml"

# Phraseapp - downloads locales to project assets folder

if [[ "$OSTYPE" == "linux-gnu" ]]; then
        curl -sL https://github.com/phrase/phraseapp-client/releases/download/1.15.0/phraseapp_linux_amd64 --output ${APP_DIR}/phraseapp
elif [[ "$OSTYPE" == "darwin"* ]]; then
        curl -sL https://github.com/phrase/phraseapp-client/releases/download/1.15.0/phraseapp_macosx_amd64 --output ${APP_DIR}/phraseapp
fi

chmod +x phraseapp

sed -i -- "s#PHRASEAPP_ACCESS_TOKEN#${PHRASEAPP_ACCESS_TOKEN}#g" ${PHRASE_APP_CONFIG}
sed -i -- "s#PHRASEAPP_PROJECT_ID#${PHRASEAPP_PROJECT_ID}#g" ${PHRASE_APP_CONFIG}
sed -i -- "s#PROJECT_ROOT#${APP_DIR}#g" ${PHRASE_APP_CONFIG}

# Download translations
./phraseapp pull
