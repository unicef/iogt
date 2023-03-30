# Overview

The page cache is provided by [Wagtail Cache][2] and is not enabled, by default. This guide leans towards Redis as the cache backend, but it should be possible to use any cache backend supported by Django 3.1.

# Activate

Set the following environment variables:

- CACHE\_BACKEND: The class that will handle the caching e.g. 'django_redis.cache.RedisCache'.
- CACHE\_LOCATION: The URL of your Redis server / cluster e.g. redis://your-redis:6379.
- CACHE\_TIMEOUT: Number of seconds until a cached entry is considered stale e.g. 300 for five minutes.

These environment variables will be used to set [cache arguments][1] in the app's Django settings.

# Deactivate

To switch off all caching features, it is sufficient to simply unset the `CACHE_BACKEND` environment variable.

# Administration

The page cache can be cleared from the Wagtail Admin by navigating to _Settings > Cache_, or _/admin/cache/_.

# In development

Most of the time it is probably desirable to switch off any sort of caching when developing the app. To avoid inadvertently committing settings that enable the page cache, it is advisable to place page cache settings in a `docker-compose.override.yml` file, if using Docker Compose.

Example Docker Compose configuration:
```docker-compose-override.yml
services:
  django:
    environment:
      CACHE_BACKEND: django_redis.cache.RedisCache
      CACHE_LOCATION: 'redis://cache:6379'
      CACHE_TIMEOUT: '300'
    depends_on:
      - cache
  cache:
    image: redis
```


[1]: https://docs.djangoproject.com/en/3.1/topics/cache/#using-a-custom-cache-backend
[2]: https://docs.coderedcorp.com/wagtail-cache/
