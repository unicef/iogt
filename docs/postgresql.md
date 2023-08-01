# Overview

By default, the development configuration uses SQLite as the relational database for the app. A more realistic production configuration might use a high performance relational database lilke PostgreSQL, and it is possible to approximate this kind of setup in development, using Docker.

# Setup

In outline:

1. Create a PostgreSQL database server
1. Configure Wagtail to use PostgreSQL
1. Apply database schema migrations

## Create a PostgreSQL database server

Create a file called `docker-compose.override.yaml` and add the following configuration into it.

```yaml
version: "3"
services:
  db:
    image: postgres:14-alpine
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: iogt
    volumes:
      - db:/var/lib/postgresql/data
      - ./initdb.d:/docker-entrypoint-initdb.d
    ports:
      - 5432:5432
volumes:
  db:
```

Start the service with `docker compose up -d db`.

## Configure Wagtail to use PostgreSQL

Create a file called `iogt/settings/local.py` and add the following configuration to it.

```python
from os import getenv

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("DB_NAME", "postgres"),
        "USER": getenv("DB_USER", "postgres"),
        "PASSWORD": getenv("DB_PASSWORD", "iogt"),
        "HOST": getenv("DB_HOST", "db"),
        "PORT": getenv("DB_PORT", "5432"),
    }
}
```

## Apply database schema migrations

Create the app database.

```sh
docker compose run --rm django manage.py migrate
```

Start the app.

```sh
docker compose up -d django
```
