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

## Share Dashboard

In Superset, anyone can view a dashboard if they have the permanent link to it, whether or not they have an account on the Superset platform. But, they can only view the data in that dashboard if they have permission to read the dataset(s) for the dashboard.

There are two things to consider when sharing a dashboard:
- Do you want your dashboard (and dataset) to be available publicly? OR only to specific, authenticated users?
- Do you want your dashboard to appear within the Superset interface, alongside the Menu buttons? OR do you want so share the dashboard without the typical Superset interface?

The first step in sharing the dashboard is sharing the dataset - either publicly, or to specific authenticated users.

The second step in sharing the dashboard is creating the permalink URL - showing the dashboard in the Superset interface, or on its own.

### How to Share a Dataset Publicly

This is a pre-requisite to publicly sharing your dashboard. Keep in mind that when you make this dataset public, hypothetically any of the data can be exposed publicly.

1. After you share your dashboard, which uses part of the data, someone may create a new dashboard from your dataset - they may or may not notice that your dataset is public - which publicly exposes other parts of your dataset that you didn't expect.

2. Other Superset users that have higher permissions, like running SQL queries against their own datasets, may also be able to use those higher permissions on your public dataset.

For this reason, it's strongly recommended to take these steps unless all data in your dataset can TRULY be made public:

1. Make a copy of your original private dataset, and label it clearly, eg "PUBLIC_Survey A_Dataset B_Dashboard Z"
2. Limit the data in this dataset to only what you need for your public dashboard visualizations
3. Adjust your dashboard to use this public dataset instead of your original private dataset

All data in this dataset should be considered viewable publicly. If someone has the URL to your dashboard, they will be able to view your visualizations without a Superset account.

- Click "Settings" menu on upper right corner
- Click on "List Roles" menu item
- Click on "edit" icon of "Public" role
- Add following permissions and save
  - can read on CssTemplate
  - can read on Chart
  - can read on Dashboard
  - can read on DashboardPermalinkRestApi
  - can dashboard permalink on Superset
  - can dashboard on Superset
  - can explore json on Superset
  - datasource access on [dataset-used-for-dashboard]

Be very careful when setting the "datasource access" permission. Make sure to choose a dataset you know can be public. If you name your public datasets starting with "PUBLIC" it will be easy to not accidentally make a private dataset public.

### How to Share a Dataset Privately

As with making datasets public, if you give a specific user access to your dataset then you should assume they can access all its data.

Anyone with both this role AND "Gamma" role will be able to view the dashboard. Anyone with both this role AND higher permissions than "Gamma" will be able to use their higher permissions to access the data, for example through SQL queries.

- Click "Settings" menu on upper right corner
- Click on "List Roles" menu item
- Click on "+" icon to add a new role and name it clearly, for example "Access to Dataset Survey A_Dataset B_Dashboard Z"
- Add following permission and save
  - datasource access on [dataset-used-for-dashboard]
- Assign this role to the user, and the "Gamma" role if they don't already have higher permissions

### How to Generate a Dashboard Link to Share Publicly or Privately

To create the URL to your dashboard, to share publicly or privately:

- Open dashboard and click "..." menu on upper right corner
- Click on "Share" menu item
- Click "Copy permalink to clipboard"

To get a fullscreen view or an embeddable view of the dashboard, without Superset menus

- Open the copied link from previous step
- Click "..." menu on upper right corner
- Click "Enter fullscreen"
- Copy the URL from address bar

To get a fullscreen/embeddable dashboard **without** its title, change standalone=true in the URL to standalone=2.

This can be useful if your dashboard title isn't very clean - for example it starts with "PUBLIC". You could use a markdown block at the top of your dashboard as an alternative header.
