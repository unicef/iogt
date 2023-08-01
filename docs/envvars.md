# Overview

The IoGT app supports environment variables as a way of changing some frequently used configuration options.

# Use with Docker

Environment variables can be defined in `docker-compose.yml`, `docker-compose.override.yml` or any custom Docker Compose configuration file. Environment variables are specified for each service, for example.

```yaml
services:
  django:
    environment:
      DB_HOST: db
```

# List of environment variables

```yaml
DB_NAME: postgres
DB_USER: postgres
DB_PASSWORD: iogt
DB_HOST: db
DB_PORT: '5432'
COMMIT_HASH: asdfghjkl
WAGTAILTRANSFER_SECRET_KEY: wagtailtransfer-secret-key
WAGTAILTRANSFER_SOURCE_NAME: iogt_global
WAGTAILTRANSFER_SOURCE_BASE_URL: https://example.com/wagtail-transfer/
WAGTAILTRANSFER_SOURCE_SECRET_KEY: wagtailtransfer-source-secret-key
VAPID_PUBLIC_KEY: ''
VAPID_PRIVATE_KEY: ''
VAPID_ADMIN_EMAIL: ''
COMMENTS_COMMUNITY_MODERATION: enable
COMMENT_MODERATION_CLASS: comments.clients.AlwaysApproveModerator
BLACKLISTED_WORDS: ''
SUPERSET_BASE_URL: ''
SUPERSET_DATABASE_NAME: ''
SUPERSET_USERNAME: ''
SUPERSET_PASSWORD: ''
PUSH_NOTIFICATION: enable
JQUERY: enable
MATOMO_TRACKING: enable
MATOMO_URL: ''
MATOMO_SITE_ID: ''
IMAGE_SIZE_PRESET: ''
```

