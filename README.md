# UI-QMako-API


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
    createdb uiqmako_db
```
5. Run local server
```
    poetry run uvicorn uiqmako_api.api.api:app
```
The API will run on: [http://localhost:8000](http://localhost:8000)
Open [http://localhost:8000/docs](http://localhost:8000/docs) or [http://localhost:8000/redoc](http://localhost:8000/redoc) to see the API docs.

6. Run tests  and coverage
```
    poetry run pytest --cov=uiqmako_api
```