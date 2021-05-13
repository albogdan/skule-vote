## Skule Vote Repo

The repository hosting the code for the [Skule Voting](https://vote.skule.ca) website.

## Contents
- [Requirements](#requirements)
- [Getting Started](#getting-started)
    * [Python Environment](#python-environment)
    * [Environment Variables](#environment-variables)

## Requirements
- Python 3.8 or higher
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

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

| **Variable**   | **Required value**                | **Default**       | **Description**                                                                   |
|----------------|-----------------------------------|-------------------|-----------------------------------------------------------------------------------|
| **DEBUG**      | 1                                 | 0                 | Run Django in debug mode. Required to run locally.                                |
| **SECRET_KEY** | Something secret, create your own | None              | Secret key for cryptographic signing. Must not be shared. Required.               |
| DB_HOST        |                                   | 127.0.0.1         | Postgres database host.                                                           |
| DB_USER        |                                   | postgres          | User on the postgres database. Must have permissions to create and modify tables. |
| DB_PASSWORD    |                                   |                   | Password for the postgres user.                                                   |
| DB_PORT        |                                   | 5432              | Port the postgres server is open on.                                              |
| DB_NAME        |                                   | hackathon_site    | Postgres database name.                                                           |
| **REACT_APP_DEV_SERVER_URL** | http://localhost:8000 |                 | Path to the django development server, used by React. Update the port if you aren't using the default 8000. |
