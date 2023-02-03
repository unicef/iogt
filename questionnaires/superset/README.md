# Apache Superset

- [Apache Superset](https://superset.apache.org) is a modern, enterprise-ready business intelligence web application. It is fast, lightweight, intuitive, and loaded with options that make it easy for users of all skill sets to explore and visualize their data, from simple pie charts to highly detailed deck.gl geospatial charts.

## Installation (Locally)
### Clone superset repo
```
git clone https://github.com/apache/superset.git
```
### Change directory
```
cd superset
```
### Launch through docker compose: 
```
docker-compose -f docker-compose-non-dev.yml pull
docker-compose -f docker-compose-non-dev.yml up
```
### Launch a specific version: 
```
git checkout 1.4.0
TAG=1.4.0 docker-compose -f docker-compose-non-dev.yml pull
TAG=1.4.0 docker-compose -f docker-compose-non-dev.yml up
```
### Log in to superset
- Open `http://localhost:8088`
- Username: `admin`
- Password: `admin`
### Connect IoGT with superset network
- Create `docker-compose.override.yml` file in the IoGT project root directory with following network
```
version: '3.5'

networks:
  default:
    name: superset_default
    external: true
```
- Start IoGT project
```
docker-compose up
```
### Connect superset with IoGT database
- Click "Settings" menu on upper right corner
- Click on "Database connections" menu item
- Click on "+ DATABASE" button, a database connection wizard will open
- Click on "PostgreSQL"
- Fill in credentials
  - HOST: `host.docker.internal`
  - PORT: `5432`
  - DATABASE NAME: `postgres`
  - USERNAME: `postgres`
  - PASSWORD: `iogt`
  - DISPLAY_NAME: "IoGT Database"
    - This will be used to connect IoGT with superset
### Create Access Roles in superset
- **Database Access Role** 
  - Click "Settings" menu on upper right corner
  - Click on "List Roles" menu item
  - Click on "+" icon to add a new role
  - Fill in 
    - Name: "IoGT Reader"
    - Permissions: 
      - database access on "IoGT Database.(id.<database-id>)"
- **Dataset Write Access Role**
  - Click "Settings" menu on upper right corner
  - Click on "List Roles" menu item
  - Click on "+" icon to add a new role
  - Fill in 
    - Name: "Write Datasets"
    - Permissions: 
      - "can write on Dataset"
### Create Users in superset
- **Service Account User - To communicate between IoGT and superset**
  - Click "Settings" menu on upper right corner
  - Click on "List Users" menu item
  - Click on "+" icon to add a new user
  - Fill in 
    - First Name: <some-name>
    - Last Name: <some-name>
    - User Name: <some-username>
    - Is Active?: checked
    - Email: <some-email>
    - Role:
      - Gamma
      - IoGT Reader
      - Write Datasets
    - Password: <some-password>
    - Confirm Password: <some-password>
- **Normal Account User**
  - Click "Settings" menu on upper right corner
  - Click on "List Users" menu item
  - Click on "+" icon to add a new user
  - Fill in 
    - First Name: <some-name>
    - Last Name: <some-name>
    - User Name: <some-username>
    - Is Active?: checked
    - Email: <some-email>
    - Role: 
      - Gamma
      - IoGT Reader
    - Password: <some-password>
    - Confirm Password: <some-password>
### Update Environment Variable for IoGT
- In `docker-compose.yml` set following environment variables
  - SUPERSET_BASE_URL: `http://superset:8088`
  - SUPERSET_DATABASE_NAME: "IoGT Database" (From connect IoGT database step)
  - SUPERSET_USERNAME: <service.account.username> (From Service Account User creation step)
  - SUPERSET_PASSWORD: <service.account.password>
### Start/Restart IoGT Project
```
docker-compose up
```
