# IoGT

Internet of Good Things ([IoGT][2]) is developed as a public good under a [BSD-2][3] open-source license.

The development uses the Python programming language, building on the [Django][4] server-side web framework combined with the [Wagtail][5] content management system.

In line with the latest Wagtail [Long Term Support release][6], IoGT 2.x supports:
- Wagtail 2.15.x
- Django 3.0.x, 3.1.x and 3.2.x
- Python 3.8, 3.9 and 3.10
- PostgreSQL, MySQL and SQLite as database backends

## Getting started

The easiest way to get started is to run IoGT using Docker. Make sure you have Docker Desktop installed, or at the very least the Docker Engine and Docker Compose (which are included in Docker Desktop).

Check out the code.
```
git clone https://github.com/unicef/iogt.git
cd iogt
```

Create the database. By default, an SQLite database will be created. This will take a few minutes on the first run because the IoGT container image needs to be created from scratch.
```
docker compose run --rm django python manage.py migrate
```

Create a superuser account for administration purposes.
```
docker compose run --rm django python manage.py createsuperuser
```

Compile .po language files stored in locale/
```
docker compose run --rm django python manage.py compilemessages
```

Start the server.
```
docker compose up -d
```

Check the logs.
```
docker compose logs -f
```

Once running, navigate to http://localhost:8000/ in your browser. Log in to the admin UI at http://localhost:8000/admin/ - use the superuser name and password you created earlier.

Shut everything down.
```
docker compose down
```

# Optional

## Setting up test data

It is possible to automatically populate the database with example data for a basic test site.

```sh
docker compose run --rm django python manage.py create_initial_data
```

Optionally, create the main menu automatically as well.

```sh
docker compose run --rm django python manage.py autopopulate_main_menus
```

## Configuring the Chatbot

Follow instructions [here](messaging/README.md)

## Configuring wagtail-transfer

It is possible to pull articles from other deployments assuming we know the secret key for that deployment.

In `iogt/settings/local.py`, define [parameters from wagtail-transfer](https://github.com/wagtail/wagtail-transfer/blob/master/docs/settings.md) as appropriate, e.g.:
```
WAGTAILTRANSFER_SECRET_KEY = 'fake_secret_key'
WAGTAILTRANSFER_SOURCES = {
   'iogt_global': {
      'BASE_URL': 'http://fake-iogt-url.org/wagtail-transfer/',
      'SECRET_KEY': 'fake_secret_key_2',
   },
}
```
Note: the names of transfer sources may only contain letters, numbers and underscores.

## Adding new localizable strings to the code base

After adding new strings to the code base that are user-facing (see https://docs.djangoproject.com/en/4.0/topics/i18n/translation/ ), follow the following process:
1. Run `./manage.py translation_tracking`
2. Review and update `common/translation_utils/translation_status.csv`. Strings that only appear in the admin backend don't need to be tagged as `translate`, only those that face users. See [here](common/translation_utils/README.md) for details.
3. Rerun `./manage.py translation_tracking`

This process updates PO files as necessary and compiles a list of strings that appear in the translation manager in the admin backend.

**Remark:** The file `common/translation_utils/translations.csv` is NOT updated in the process.
Even though it has a column "is in use", its data is currently not updated automatically, and similarly, new strings are not added automatically.

## Apache Superset Setup and Configuration
- See [here](questionnaires/superset/README.md)

## Page caching

Page caching is provided by Wagtail Cache and is deactivated by default. To start caching pages, follow the [activation intructions][7].

## Elasticsearch

To use Elasticsearch as a search backend instead of the relational database see the [setup instructions][11].

## Migrating content from IoGT v1
Follow instructions [here](iogt_content_migration/README.md)

## Add/Update Package
Follow instructions [here][10]

# Running Tests

Run the following commands:
```
make tests
make selenium-test
```

In parallel, for example, with 4 processes:
```
IOGT_TEST_PARALLEL=4 make test
IOGT_TEST_PARALLEL=4 make selenium-test
```

More details of the Selenium tests can be found in the [Selenium test README][9].


[1]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
[2]: https://www.unicef.org/innovation/IoGT
[3]: https://github.com/unicef/iogt/blob/develop/LICENSE
[4]: https://www.djangoproject.com/
[5]: https://wagtail.io/
[6]: https://github.com/wagtail/wagtail/wiki/Release-schedule
[7]: ./docs/cache.md
[8]: ./docs/troubleshooting.md
[9]: ./selenium_tests/README.md
[10]: ./docs/dependency-management.md
[11]: ./docs/elasticsearch.md
