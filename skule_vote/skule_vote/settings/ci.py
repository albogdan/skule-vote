"""
Settings file for use in testing and CI environments.

Usage:
    ```
    python manage.py test --settings=hackathon_site.settings.ci
    ```

Changes the default database to use an in-memory sqlite3 database,
instead of the default postgresql database. This means that you
don't need to have access to a properly configured postgres server
to run tests (helpful in CI environments especially, though it is
possible to use a postgres image for GitHub actions), and tests
will be faster without the round-trips to the database.

The caveat is that there may be inconsistencies between sqlite and
postgres, that would pose an issue in production but will not be
caught during testing. These should be caught by a staging environment,
and by running your code before you merge it.
"""
from skule_vote.settings import *

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
