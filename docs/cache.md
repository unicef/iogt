# Overview

IoGT has performance features that can be enabled when a distributed cache, like Redis, is available, including:

- A page cache, provided by [Wagtail Cache][2].
- A cache for Wagtail image renditions
- A general-purpose 'default' cache

It is strongly recommended to use Redis as the cache backend, but it should be possible to use any cache backend supported by Django 3.1.

# Activate

Set the following environment variables:

- CACHE: Set to 'enable' to activate caching
- CACHE\_LOCATION: The URL of your Redis server / cluster e.g. redis://your-redis:6379.

Optionally set:

- CACHE\_BACKEND: Only change this if you know what you are doing. Default: 'wagtailcache.compat\_backends.django\_redis.RedisCache' [3]
- CACHE\_KEY\_PREFIX: Useful for partioning the key space if sharing a Redis instance; each IoGT instance can have a different prefix to avoid interference. Set to empty string ('') to disable prefixing. Default: random UUID
- CACHE\_TIMEOUT: Number of seconds until a cached entry is considered stale. Default: '300'.

These environment variables will be used to set [cache arguments][1] in the app's Django settings.

# Deactivate

To switch off caching features, simply unset the `CACHE` environment variable or set it to anything but 'enable'.

# Administration

The page cache can be cleared from the Wagtail Admin by navigating to _Settings > Cache_, or _/admin/cache/_.

# In development

Most of the time it is probably desirable to switch off any sort of caching when developing the app. To avoid inadvertently committing settings that enable the page cache, it is advisable to place page cache settings in a `docker-compose.override.yml` file, if using Docker Compose.

Example Docker Compose configuration:
```docker-compose-override.yml
services:
  django:
    environment:
      CACHE: enable
      CACHE_KEY_PREFIX: ''
      CACHE_LOCATION: redis://cache:6379
      CACHE_TIMEOUT: '300'
    depends_on:
      - cache
  cache:
    image: redis
```


[1]: https://docs.djangoproject.com/en/3.1/topics/cache/#using-a-custom-cache-backend
[2]: https://docs.coderedcorp.com/wagtail-cache/
[3]: https://docs.coderedcorp.com/wagtail-cache/getting_started/supported_backends.html#django-redis
