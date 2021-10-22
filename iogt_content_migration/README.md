# IoGT v1 to v2 content migration

## Development

### Prerequisites

- v1 database backup
```
pg_restore --clean --if-exists --file=backup.sql --no-owner <path-to-backup>
```
- v1 media directory
- up-to-date v2 app with all db migrations run

### Getting started

Make sure you are in the iogt project root directory.
Create a directory called 'legacy-initdb.d'.
Add the v1 database backup (SQL) file in 'legacy-initdb.d'. It will be automatically loaded from this location when the legacy database is started.
Start the legacy database with docker-compose:
```
docker-compose -f docker-compose-legacy-db.yml up
```
Execute the migration commands in the following order:
```
./manage.py load_v1_db --password iogt --media-dir <path to media dir backup>
./manage.py load_v1_users --password iogt 
```
Run with the help flag to see more options:
`./manage load_v1_db --help`
```
  -h, --help            show this help message and exit
  --host HOST           IoGT V1 database host
  --port PORT           IoGT V1 database port
  --name NAME           IoGT V1 database name
  --user USER           IoGT V1 database user
  --password PASSWORD   IoGT V1 database password
  --media-dir MEDIA_DIR
                        **RELATIVE Path** to IoGT v1 media directory
  --skip-locales        Skip data of locales other than default language
  --delete-users        Delete existing Users and their associated data. Use carefully
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.

```

`load_v1_users --help`
```
  -h, --help            show this help message and exit
  --host HOST           IoGT V1 database host
  --port PORT           IoGT V1 database port
  --name NAME           IoGT V1 database name
  --user USER           IoGT V1 database user
  --password PASSWORD   IoGT V1 database password
  --skip-locales        Skip data of locales other than default language
  --delete-users        Delete existing Users and their associated data. Use carefully
  --group-ids GROUP_IDS [GROUP_IDS ...]
                        Groups IDs to mark registration survey mandatory for
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```


## Test / Staging / Production

TBD
