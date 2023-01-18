# Switch on

Set the following environment variables:
```
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://redis:6379
CACHE_TIMEOUT=300
```

These environment variables will be used to set [cache arguments][1] in the app's Django settings.

# Administration

The page cache is provided by [Wagtail Cache][2]. The page cache can be cleared from the Wagtail Admin by navigating to _Settings > Cache_, or _/admin/cache/_.

# Switch off

To switch off all caching features, it should be sufficient to simply unset the `CACHE_BACKEND` environment variable.

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
    image: redis:6.2-buster
```


[1]: https://docs.djangoproject.com/en/3.1/topics/cache/#using-a-custom-cache-backend
[2]: https://docs.coderedcorp.com/wagtail-cache/
