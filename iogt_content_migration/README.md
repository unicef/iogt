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
Execute the migration command:
```
./manage.py load_v1_db --password iogt --media-dir <path to media dir backup>
```
Run with the help flag to see more options:
```
./manage load_v1_db --help
```

## Test / Staging / Production

TBD
