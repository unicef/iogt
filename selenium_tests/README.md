# Selenium Tests

We are using Selenium to carry out functional testing in the IoGT project. Specifically, we are using Selenium Grid which gives us the option to run tests on multiple browsers.

The functional tests have been broken down into Categories > Groups > Tests.

- Each category has its own folder within the `selenium_tests` directory and contains multiple groups of tests
- Each group of tests has its own Python file within the category folder, each group contains multiple tests

For general guidance on how to write Selenium tests, review the existing tests within this folder.

## Running tests locally

The tests are configured to run automatically through GitHub actions, although this may not be practical during intial test development.

The Selenium Grid and WebDriver is run from a Docker container. Therefore, to run tests locally you need to install Docker and have it running on your computer.

Then run the following commands:
```
make selenium-up
```
This starts up the docker containers required for testing.

To run the tests themselves, run:
```
make selenium-local
```

You can view the tests as they run locally via [a couple of different methods][1] - namely VNC and noVNC.

## Running tests in parallel

Make sure that no ports are being exposed from the Selenium nodes. For example, don't use the 'ports' option to expose the VNC port (5900) because this will prevent two or more Selenium nodes from starting by causing them all try to bind to port 5900 on the host.

Scale up the number of Selenium nodes.
```
docker-compose -f docker-compose.selenium.yml up -d --scale chrome=4
```

Run the tests in parallel.
```
docker-compose -f docker-compose.selenium.yml exec -T django python manage.py test selenium_tests --parallel 4
```

The environment variable `IOGT_TEST_PARALLEL` when running the whole test suite.
```
IOGT_TEST_PARALLEL=4 make selenium-test
```

## Architecture

App service container starts and sleeps - waiting for test executions. A sleeping service is required so that the Selenium nodes can target the test server that is started by the test suite.

PostgreSQL service - used instead of Sqlite for better multi-threaded performance and for being more like a production environment.

Selenium Hub - to route webdriver commands to Selenium nodes

Selenium Nodes - currently only Chrome, but other nodes with different browsers and capabilities could be created e.g. Firefox, Safari, Edge, or with Javascript disabled and/or mobile features enabled.

Once all services are started, test executions can be started on the app service. Each test execution starts a test app server, creates a new test database, then begins running tests. When run in parallel, the main test runner will start several child test runners that each create their own test server and database, and requires a single Selenium node to run tests in.


[1]: https://github.com/SeleniumHQ/docker-selenium#debugging
