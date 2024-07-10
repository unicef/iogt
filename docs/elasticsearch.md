# Overview

Wagtail supports the use of a relational database or Elasticsearch as a search backend. A relational database is sufficient for simple search queries and sites that do not require high performance. Elasticsearch allows the search capability to be scaled up and removes the burden of searching from the relational database.

By default, the relational database backend is used and there is no need for further configuration. The rest of this guide will explain how to set up Elasticsearch as a search backend.

# Setup

The outline of the setup process is as follows.

1. Create an Elasticsearch cluster
1. Configure Wagtail to use Elasticsearch
1. Create the search index

## Create Elasticsearch cluster

Create the file `docker-compose.override.yml`. Add the following to the file.

```yaml
services:
  search:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.12.1
    environment:
      - discovery.type=single-node
    volumes:
      - search:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
volumes:
  search:
```

If you already have a `docker-compose.override.yml`, you will need to merge the snippet above into it.

## Configure Wagtail to use Elasticsearch

Create the file `iogt/settings/local.py`. Add the following to the file.

```python
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.elasticsearch7',
        'URLS': ['http://search:9200'],
        'INDEX': 'iogt',
        'TIMEOUT': 5,
        'OPTIONS': {},
        'INDEX_SETTINGS': {},
        'AUTO_UPDATE': True,
        'ATOMIC_REBUILD': True
    }
}
```

More information about the available configuration options can be found in the [search backends] section of the Wagtail documentation.

## Create the search index

To create and subsequently update the ElasticSearch index.

```sh
docker compose run --rm django python manage.py update_index
```

If the search function does not return any results for any search, it may be necessary to update the index. This applies whether or not Elasticsearch is used.


[search backends]: https://docs.wagtail.org/en/v3.0.3/topics/search/backends.html
