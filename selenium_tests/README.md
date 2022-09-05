# Selenium Tests

We are using Selenium to carry out functional testing in the IoGT project. Specifically, we are using Selenium grid which gives us the option to run tests on multiple browsers.

The functional tests have been broken down into Categories > Groups > Tests.

- Each category has its own folder within the `selenium_tests` directory and contains multiple groups of tests
- Each group of tests has its own Python file within the category folder, each group contains multiple tests

For general guidance on how to write Selenium tests, review the existing tests within this folder.

## Running tests locally

The tests are configured to run automatically through GitHub actions, although this may not be practical during intial test development.

The Selenium Grid and WebDriver is run from a Docker container. Therefore, to run tests locally you need to install Docker Desktop and have it running on your computer.

Then run the following commands:
```
make selenium-up
```
This starts up the docker containers required for testing.

To run the tests themselves, run:
```
make selenium-local
```

You can view the tests as they run locally using a number of [different methods][1].


[1]: https://github.com/SeleniumHQ/docker-selenium#using-a-vnc-client
