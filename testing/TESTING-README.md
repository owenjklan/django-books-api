# Testing AutoDojo
Because the whole point of AutoDojo is to programmatically define the
CRUD endpoints of a Ninja application from the Model specification alone,
we need some way to test the behaviour of actual endpoints. Django's test
client could be used, but for our purposes, we're going to run the test
application ("books API") in a Docker container and use Postman collections,
run by Newman, to perform our suites of tests against the generated
APIs.

---
**TODO:** Provide the ability to select (by Environment variable) one of
multiple NinjaAPI() configurations (for custom configs etc) and provide
separate Postman Collections as appropriate
---

## Building and launching the Docker container
Build the latest Docker image like so (assuming running from
repository root):
```shell
docker build . -t books-api:latest
```

If that has worked, you can run the image with command like this:
```shell
docker run -d -p 8000:8000 --name autodojo-test-app books-api:latest
```

**NOTE:**
- The image runs the `clean_start.sh` script as it's entrypoint command.
  This script ensures that a new `db.sqlite3` database file is created and
  then runs `manage.py migrate` against it.
- The above point means that if you make any modifications and migrations
  to the database schema, you'll need to rebuild the Docker image to have
  these migrations applied.

## Running testing Postman collections
The `run_test_collection.sh` script can be used to provide a short-hand to
run a Postman collection with the appropriate environment file. The run
is performed using Newman.

The `postman` directory should contain exported Postman Collections as
well as matching Environments. For example, `run_test_collection.sh foobar`
will launch Newman, expecting to run the collection defined in `foobar.collection.json`,
and providing an environment defined inside `foobar.environment.json`.

