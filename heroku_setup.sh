#!/bin/bash

function setupHeroku {
    # creates new heroku app
    heroku create
    # adds the postgres addon as a database
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
}

setupHeroku



