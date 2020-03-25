Example connexion application [![Build Status](https://travis-ci.com/mgetka/connexion-example.svg?branch=master)](https://travis-ci.com/mgetka/connexion-example) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
======================================

This project serves as an example of [connexion](https://github.com/zalando/connexion) application.
It also utilizes [SQLAlchemy](https://www.sqlalchemy.org/) and [alembic](https://alembic.sqlalchemy.org/en/latest/).
It provides simple API allowing for creation and management of rated entries about programming
languages, libraries, databases and other IT related entities. More broad description of the API is
contained in [OpenAPI 3 document](src/conexample/api/rest/api.yml). The documentation can be
explored via swagger UI accessible at `/v1/ui/` after running the application.

Internally, the application is organized utilizing elements of clean architecture paradigm. There is
core object implementing application domain logic and adapters objects implementing interfaces for
databases and implementing the API itself. Interactions between said objects are limited to the
interfaces specified in [interfaces.py](src/conexample/interface.py) file.

In connexion, `operationId`s defined in the OpenAPI document are mapped to endpoint callables defined in
the project. In this application, custom mapper (or _resolver_ in the connexion nomenclature) is
implemented. It maps structured `operationId`s onto static methods arranged in the nested classes
structure. The implementation is contained in [`api.rest`](src/conexample/api/rest/__init__.py) adapter
class.

## Configuration

Configuration is provided via environment variables.

| Variable                       | Default                                    | Description                                                                                                                                                                     |
| ------------------------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CONEXAMPLE_CONFIG`            | n/a                                        | Config file path - more details below                                                                                                                                           |
| `LOGGING_LEVEL`                | `info`                                     | Logging level. Can be one of: `debug`, `info`, `warning`, `error`, `critical`                                                                                                   |
| `DATABASE_SQL_DATABASE_URI`    | `postgresql://postgres@localhost/postgres` | SQLAlchemy database URL (see: [database urls](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls))                                                               |
| `DATABASE_SQL_CONNECTION_POOL` | `5`                                        | Database connection pool size                                                                                                                                                   |
| `DATABASE_SQL_POOL_OVERFLOW`   | `10`                                       | Maximum overflow size of the database connection pool (see [QueuePool docs](https://docs.sqlalchemy.org/en/13/core/pooling.html#sqlalchemy.pool.QueuePool.params.max_overflow)) |

Config parameters are handled via [python-dotenv](https://github.com/theskumar/python-dotenv)
package. Config variables can be stored in `.env` file that will be loaded to the environment on
application startup. Following list presents config sources precedence:

 1. Environment variables
 2. `.env` file contents
 3. Default values

## Migrations

Database schema and data migrations are managed with the use of alembic tool. The tool will not try
to create database, so before running the application, database needs to already exist. In the case
of docker image, migrations are checked on each application start. To run them manually one needs to
execute following command

```
alembic -c migrations/alembic.ini upgrade head
```

Please note that, alembic takes database engine config from the same source as the whole
application, so if `DATABASE_SQL_DATABASE_URI` value is not present in the environment the migration
will fail.

## Requirements

The application requires `python>=3.7`.

## Installation and running

To install execute

```
python setup.py install
```

to run in development mode

```
conexample-dev
```

or with auto reloading

```
./run_debug.py
```

In the production environment application should be run via WSGI server. The WSGI application object
is located at `conexample.wsgi.api:app`. Example uWSGI configuration is provided in [uwsgi.yml](uwsgi.yml).

## Docker

The application can be run in the scope of docker container. Provided docker image defines
following, additional, configuration arguments:

| Variable          | Default        | Description        |
| ----------------- | -------------- | ------------------ |
| `UWSGI_BIND`      | `0.0.0.0:5000` | uWSGI bind address |
| `UWSGI_PROCESSES` | `2`            | uWSGI processes    |
| `UWSGI_PROTOCOL`  | `http`         | uWSGI protocol     |

Conveniently, the application can be run with the use of docker-compose

```
docker-compose up
```

## Testing

To run tests install the application and development dependencies

```
python setup.py develop
pip install -e '.[dev]'
```

then run tests

```
pytest --cov=conexample --cov-report term-missing test
```
