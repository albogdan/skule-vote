## Skule Vote Repo

The repository hosting the code for the [Skule Voting](https://vote.skule.ca) website.

## Contents

- [Requirements](#requirements)
- [Getting Started](#getting-started)
  - [Python Environment](#python-environment)
  - [Environment Variables](#environment-variables)
  - [Running the development server](#running-the-development-server)
  - [Creating users locally](#creating-users-locally)
  - [TLDR of the above](#tldr-of-the-above)
- [Working with the Admin Site](#working-with-the-admin-site)
  - [Creating ElectionsSessions with CSV Files](#method-1-using-a-csv-file-recommended)
  - [Creating ElectionSessions Manually](#method-2-manually)

## Requirements

- Python 3.8 or higher
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### Python Environment

For local development, create a Python virtual environment.

#### Conda

We recommend you use [Anaconda](https://www.anaconda.com/products/individual) (or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)), as it makes managing virtual environments with different Python versions easier:

```bash
$ conda create -n skule_vote python=3.9
```

This will create a new conda environment named `skule_vote` (you may choose a different name). Then, activate the environment:

```bash
$ conda activate skule_vote
```

#### venv

Alternatively, you can use [venv](https://docs.python.org/3/library/venv.html) provided under the standard library, but note that you must already have Python 3.9 installed first:

```bash
$ python3.9 -m venv venv
```

How you activate the environment depends on your operating system, consult [the docs](https://docs.python.org/3/library/venv.html) for further information.

#### Installing Requirements

Install the requirements in `skule_vote/requirements.txt`. This should be done regularly as new requirements are added, not just the first time you set up.

```bash
$ cd skule_vote
$ pip install -r requirements.txt
```

### Environment Variables

In order to run the django and react development servers locally (or run tests), the following environment variables are used. Those in **bold** are required.

| **Variable**                 | **Required value**                | **Default**    | **Description**                                                                                                                                             |
| ---------------------------- | --------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DEBUG**                    | 1                                 | 0              | Run Django in debug mode. Required to run locally.                                                                                                          |
| **SECRET_KEY**               | Something secret, create your own | None           | Secret key for cryptographic signing. Must not be shared. Required.                                                                                         |
| DB_HOST                      |                                   | 127.0.0.1      | Postgres database host.                                                                                                                                     |
| DB_USER                      |                                   | postgres       | User on the postgres database. Must have permissions to create and modify tables.                                                                           |
| DB_PASSWORD                  |                                   |                | Password for the postgres user.                                                                                                                             |
| DB_PORT                      |                                   | 5432           | Port the postgres server is open on.                                                                                                                        |
| DB_NAME                      |                                   | skule_vote     | Postgres database name.                                                                                                                                     |
| **REACT_APP_DEV_SERVER_URL** | http://localhost:8000             |                | Path to the django development server, used by React. Update the port if you aren't using the default 8000.                                                 |
| CONNECT_TO_UOFT              |                                   | 0              | If set, tries to obtain voter information by connecting to the UofT endpoint. Disabled by default to allow for testing, but must be enabled for production. |
| UOFT_SECRET_KEY              |                                   | 0              | Used to verify the integrity of voter data sent by UofT. Only used when `CONNECT_TO_UOFT == 1`                                                              |

If you are using miniconda, you can add these to your environment such that each time you `conda activate skule_vote`, the variables will be sourced as well. To do this run (while the skule_vote environment is activated):

```bash
$ conda env config vars set DEBUG=1
```

where you can substitube `DEBUG=1` for any environment variable you desire.

### Running the development server

#### Database

Before the development server can be ran, the database must be running. This project is configured to use [PostgreSQL](https://www.postgresql.org/).

You may install Postgres on your machine if you wish, but we recommend running it locally using docker. A docker-compose service is available in `development/docker-compose.yml`. To run the database:

```bash
$ docker-compose -f development/docker-compose.yml up -d
```

To shut down the database:

```bash
$ docker-compose -f development/docker-compose.yml down
```

The postgres container uses a volume mounted to `development/.postgres-data/` for persistent data storage, so you can safely stop the service without losing any data in your local database.

A note about security: by default, the Postgres service is run with [trust authentication](https://www.postgresql.org/docs/current/auth-trust.html) for convenience, so no passwords are required even if they are set. You should not store any sensitive information in your local database, or broadcast your database host publicly with these settings.

#### Database migrations

[Migrations](https://docs.djangoproject.com/en/3.0/topics/migrations/) are Django's way of managing changes to the database structure. Before you run the development server, you should run any unapplied migrations; this should be done every time you pull an update to the codebase, not just the first time you set up:

```bash
$ cd skule_vote
$ python manage.py migrate
```

#### Run the development server

Finally, you can run the development server, by default on port 8000. From above, you should already be in the top-level `skule_vote` directory:

```bash
$ python manage.py runserver
```

If you would like to run on a port other than 8000, specify a port number after `runserver`.

### Creating users locally

In order to access most of the functionality of the site (the React dashboard or otherwise), you will need to have user accounts to test with.

To start, create an admin user. This will give you access to the admin site, and will bypass all Django permissions checks:

```bash
$ python manage.py createsuperuser
```

Once a superuser is created (and the Django dev server is running), you can log in to the admin site at `http://localhost:8000/admin`. Note that creating a superuser does not give it a first or last name, so you should set those from the admin site otherwise some parts of the site may behave weird. Our regular sign up flow also assumes that username and email are the same, so we recommend creating your superuser accordingly.

### TLDR of the above
If you're on Mac or Linux, copy and paste the following in the top-level `skule_vote` directory:

Start the Django server in terminal 1:

```bash
conda activate skule_vote
export SECRET_KEY=<your key>
export DEBUG=1
export REACT_APP_DEV_SERVER_URL=http://localhost:8000
docker-compose -f development/docker-compose.yml up -d
cd skule_vote/
python manage.py migrate
python manage.py runserver
```

Start the React app in terminal 2:

```bash
cd skule_vote/frontend/ui
yarn start
```

Assuming you are using all default ports:
- Access the Django admin site at [http://127.0.0.1:8000](http://127.0.0.1:8000)
- View the React app at [http://localhost:3000](http://localhost:3000)
- To use the frontend, create a cookie to authenticate yourself at [http://localhost:8000/api/bypasscookie](http://localhost:8000/api/bypasscookie)

## Working with the Admin Site

The admin site can be found at `/admin` (for login credentials enquire with the previous CRO) and is used to set up `ElectionSessions`, `Elections`, `Candidates` for each `Election` and `Eligibilities` for each `Election`. These can be done either manually or automatically using a CSV file. Note that there are templates for how these files must appear in the `skule_vote/backend/static/backend/csv_templates` folder of this repo.

Additionally, if you go to the admin site and click on `Election Sessions` on the left-hand panel, you will get a page that shows you a list of all the `Election Sessions`. On top right this page you will see a button `Download CSV Templates` that will serve you a ZIP file of all of the CSV files in the `skule_vote/backend/static/backend/csv_templates` directory.

**Developer Note**: If you wish to change the CSV templates in any way, make sure to regenerate the ZIP file and place it in the `skule_vote/backend/static/backend` directory.

## Notes on Committing Backend Changes

To run all unit tests, run `python manage.py test`. You can learn more about writing and running unit tests in [Django documentation](https://docs.djangoproject.com/en/3.2/topics/testing/overview/).

All python code is formatted using [Black](https://github.com/psf/black). To format your code, simply run `black .` in the project root. To format a specific file, run `black FILE.py`.

**You can only merge PRs if all unit tests are passing and your code is fully formatted with Black.**

If you have changed a model, you need to run `python manage.py makemigrations` to generate the required migrations to translate that change to the DB. Otherwise, tests will fail and the website will not work.

## Setting up an Election Session

### Method 1: Using a CSV File (Recommended)

To use this method, when you go to the `admin` site and add an `ElectionSession` you must add an `ElectionSession` with a `name`, `start_date` and `end_date`, and CSV files for each section of `election`, `candidate` and `eligibility`. These CSV files have certain constraints that must be obeyed. The constraints are as follows:

- The header (first row) of each CSV file must be the same as the ones in the `/csv_files` templates.
- Within a single CSV file all rows must be of equal length (have the same number of comma separated values).
- Election and Eligibility CSVs must have the same number of rows, since they are 1-to-1.
- The Election names in the Eligibilities and Candidates CSVs must match the ones in the Elections CSV.
- Within the Elections CSV:
  - All of the `seats_available` must be integers and >=1.
  - Election Categories must be one of `[Referenda, Officer, Board of Directors, Discipline Club, Class Representative, Other]`.
- Within the Eligibilities CSV:
  - All of the eligible fields must be integers and either `1 (True)` or `0 (False)`.
  - Eligibilities `status_eligible` fields must be one of `[Full Time, Part Time, Full and Part Time]`.

**Note**: All the CSV files must be uploaded at once, or none at all. If this is not met then an error will be shown and nothing will happen.

**Note**: if you upload CSVs successfully and realize you made a mistake, you can just re-upload the updated CSVs to the same `ElectionSession`. All of the previous `Elections`, `Candidates` and `Eligibilities` _connected to that `ElectionSession`_ will be deleted and new ones will be created from the new CSV.

**Note**: once an ElectionSession has started you _cannot_ edit it to change its `name`, `start_date`, or upload any new CSV files. Any changes required for `Elections`, `Candidates` and `Eligibilities` must be made manually. You _can_ change the `ElectionSession's` `end_date` once it has started, also manually.

### Method 2: Manually

To use this method, when you go to the `admin` site and add an `ElectionSession` you must add an `ElectionSession` with only a `name`, `start_date` and `end_date`. You will then go and manually create each of `Election`, `Candidate` and `Eligibility`. Note that `Candidate` and `Eligibility` require an `Election` to connect to, so `Elections` should be created first.

## Notes on the RON/No Candidate

The `RON/No Candidate` is created by default on the creation of each `Election`. It is also deleted by cascade on deletion of any `Election`, which includes manual `Election` deletion or as a cascade from deleting an `ElectionSession`. We describe it as the `RON/No Candidate` since it can take the form of a `RON Candidate` in the case where there are two or more other `Candidates`, or the `No Candidate` in the case of a single other `Candidate`.

The `RON/No Candidate` has a default statement that says `Choose this option if you don’t believe there are suitable candidate(s). If 'Reopen Nominations' wins, nominations for this position will be re-opened so that more candidates can run.`. This will appear to the user when `RON` is active. When `No` is active, we remove the message and change the name to `No`. This is all done in the frontend.

The `RON/No Candidate` is protected from accidental deletion in the following ways:

- When you go to the `Candidate` changelist on the admin site, you will not see any `RON Candidates` when in production more (you will see them in debug mode though).
- When you go to the change view for a specific `Candidate` on the admin site, you should not see a `Delete` button for any `RON Candidates`, while you can see it for regular `Candidates` (you will see them in debug mode though).

**Developer Note: If you wish to change any of these options they are found in the `backend/models.py` and `backend/admin.py` files.**
