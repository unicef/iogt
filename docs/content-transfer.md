# Content transfer

Articles can be transferred from other IoGT sites via Wagtail Transfer - the [documentation][1] explains how to execute transfers. The source and destination sites need to be configured correctly to enable content transfers.

## Setup

For simple situations where content will always be transferred from a single source site, it is probably best to configure using environment variables. For more complex scenarios, it may be necessary to use a local Python configuration file.

To prevent unauthorised access, the source site must set a secret key, which must be shared with any sites that will pull content from the source.

### Environment variables

The source site configuration is simpler. It is only necessary to set the secret key.

```
WAGTAILTRANSFER_SECRET_KEY=secret_key
```

The secret key should be a random string of characters - the longer the better.

The destination site configuration needs to describe how to communicate with the source site.

```
WAGTAILTRANSFER_SOURCE_NAME=iogt_source
WAGTAILTRANSFER_SOURCE_BASE_URL=https://example.com/wagtail-transfer/
WAGTAILTRANSFER_SOURCE_SECRET_KEY=secret_key
```

The 'source secret key' needs to be the same as the 'secret key' set at the source site. The 'source name' will appear in the Wagtail Admin user interface to help users to identify the source site - it may only contain letters, numbers and underscores.

### Local Python file

The source site may still be configured using environment variables i.e. to set the secret key. If that is all that is required, it is recommended to use environment variables.

If environment variables are not sufficient, a local Python file should be used to override the default configuration.

Create a file called `iogt/settings/local.py`. Define [parameters from wagtail-transfer].

```python
# Required for source site only
WAGTAILTRANSFER_SECRET_KEY = "secret_key"

# Multiple sources could be defined at the destination site
WAGTAILTRANSFER_SOURCES = {
   "iogt_source": {
      "BASE_URL": "http://example.com/wagtail-transfer/",
      "SECRET_KEY": "secret_key",
   },
}
```


[1]: https://wagtail.github.io/wagtail-transfer/
[parameters from wagtail-transfer]: https://github.com/wagtail/wagtail-transfer/blob/master/docs/settings.md
