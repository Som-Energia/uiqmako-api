# UI-QMako-API

[![CI Status](https://github.com/Som-Energia/uiqmako-api/actions/workflows/integration_config.yml/badge.svg)](https://github.com/Som-Energia/uiqmako-api/actions/workflows/integration_config.yml)
[![Coverage Status](https://coveralls.io/repos/github/Som-Energia/uiqmako-api/badge.svg?branch=master)](https://coveralls.io/github/Som-Energia/uiqmako-api?branch=master)


API of Som Energia UI-QMako tool.

UI-QMako allows for a user friendly editing of Mako Templates.

## Getting started
### Python version

Python 3.8.8

### Dependencies

* Git.
* Python 3, pip and [poetry](https://python-poetry.org/).

### Installation and run

1. Clone project from repo
```
    git clone git@github.com:Som-Energia/uiqmako-api.git
```
2. Setup poetry environment Python
```
    cd uiqmako-api
    poetry install
```
3. Create local configuration
```
    cp .env.example .env
    # Review and edit .env
```
4. Create database
```
    # If you didn't do that before for your user, here 'myuser'
    sudo su postgres
    createuser myuser
    echo "ALTER USER myuser CREATEDB" > psql
    exit

    # and then
    createdb uiqmako_db
```
5. Run development server
```
    poetry run uvicorn uiqmako_api.api.api:app --debug
```

The API will run on: [http://localhost:8000](http://localhost:8000)

Open [http://localhost:8000/docs](http://localhost:8000/docs) or [http://localhost:8000/redoc](http://localhost:8000/redoc) to see the API docs.

6. Run tests  and coverage

```
    createdb test_uiqmako
    # Review and edit test/.env.test
    poetry run pytest -v --cov=uiqmako_api
```
