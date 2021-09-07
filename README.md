# IoGT

Internet of Good Things ([IoGT][2]) is developed as a public good under a [BSD-2][3] open-source licence.

The development uses the Python programming language, building on the [Django][4] server-side web framework combined with the [Wagtail][5] content management system.

In line with the latest Wagtail [Long Term Support release][6], IoGT 2.x supports:
- Wagtail 2.11.x
- Django 2.2.x, 3.0.x and 3.1.x
- Python 3.6, 3.7, 3.8 and 3.9
- PostgreSQL, MySQL and SQLite as database backends

## Getting started

If you'd like to contribute to IoGT development, the best way to get started is to clone a copy of this repository and run the code on your machine.
```
git clone https://github.com/unicef/iogt.git
cd iogt
```

Create an [isolated Python environment][1], into which we will install the project's dependencies. This is highly recommended so that the requirements of this project don't interfere with any other Python environments you may have in your system, including the global Python environment. We also recommend that you create a new environment outside of the project directory. 
```
python3 -m venv <path_to_venv_dir>
source <path_to_venv_dir>/bin/activate
pip install -r requirements.txt
```

Create the database. By default, an SQLite database will be created.
```
./manage.py migrate
```

Create a super user account for administration purposes.
```
./manage.py createsuperuser
```

Compile .po language files stored in locale/
```
./manage.py compilemessages
```

Finally, start the server.
```
./manage.py runserver
```

Once running, navigate to http://localhost:8000 in your browser.


### Running ElasticSearch (Optional)

1. Set up an elastic search cluster
2. Update local.py to use Elasticsearch as the backend. More details [here](https://docs.wagtail.io/en/stable/topics/search/backends.html#elasticsearch-backend)
   
   ```
   WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch7',
        'URLS': ['http://localhost:9200'],
        'INDEX': 'iogt',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
        'AUTO_UPDATE': True,
        'ATOMIC_REBUILD': True
        }
   }
   ```

3. Run `./manage.py update_index` to update the ElasticSearch Index

### Setting up test data

It is possible to automatically populate the database with example data for a basic test site.
```
./manage.py create_initial_data
```

Optionally, create the main menu automatically as well.
```
./manage.py autopopulate_main_menus
```


### Running Tests
```
./manage.py test --settings=iogt.settings.test
```

## Setup with Docker Compose
You can choose to set up the project locally using Docker Compose. This setup is recommended if you 
want to replicate the production environment

### Steps

Clone the repository

```
git clone https://github.com/unicef/iogt.git
```
Run setup command. This will set up the database and also update the ElasticSearch Index.
```
cd iogt
make setup
```

Create a super user account for administration purposes.
```
docker-compose run django python manage.py createsuperuser
```

Run the compose file
```
make up
```
You're all set now. See the `Makefile` for other commands related to docker-compose

## Setting up test data

It is possible to automatically populate the database with example data for a basic test site.
```
docker-compose run django python manage.py create_initial_data
```

Optionally, create the main menu automatically as well.
```
docker-compose run django python manage.py autopopulate_main_menus
```

## Migrating content from IoGT v1
Follow instructions [here](iogt_content_migration/README.md)

## Running Tests
Run the following command:
```
make test
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
      'BASE_URL': 'http://fake-iogt-url.org',
      'SECRET_KEY': 'fake_secret_key_2',
   },
}
```
Note: the names of transfer sources may only contain letters, numbers and underscores.


[1]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
[2]: https://www.unicef.org/innovation/IoGT
[3]: https://github.com/unicef/iogt/blob/develop/LICENSE
[4]: https://www.djangoproject.com/
[5]: https://wagtail.io/
[6]: https://github.com/wagtail/wagtail/wiki/Release-schedule

## Cypress Tests
```
make cypress
cd cypress_tests/
npm install
node_modules/.bin/cypress open
```
