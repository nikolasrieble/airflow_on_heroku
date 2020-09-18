#!/bin/bash

function setupHeroku {

    # remove any existing heroku remote of this repo
    git remote remove heroku

    local RandomNamePart
    RandomNamePart=$(openssl rand -hex 8)
    heroku create "airflow-$RandomNamePart"

    heroku addons:create heroku-postgresql:hobby-dev

    local DATABASE_CONN
    DATABASE_CONN=$(heroku config:get DATABASE_URL)
    heroku config:set AIRFLOW__CORE__SQL_ALCHEMY_CONN="$DATABASE_CONN"

    heroku config:set AIRFLOW__CORE__LOAD_EXAMPLES=False
    heroku config:set AIRFLOW_HOME=/app

    local FERNET_KEY
    FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    heroku config:set AIRFLOW__CORE__FERNET_KEY="$FERNET_KEY"

    git push heroku master

    heroku config:set AIRFLOW__WEBSERVER__AUTHENTICATE=True
    heroku config:set AIRFLOW__WEBSERVER__AUTH_BACKEND=airflow.contrib.auth.backends.password_auth

    heroku run "python initial_user_creation.py"

    heroku run "rm initial_user_creation.py"
}

setupHeroku



