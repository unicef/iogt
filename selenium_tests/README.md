# Selenium Tests

We are using Selenium to carry out functional testing on the iogt site. Specifically we are using Selenium grid which gives us the option to run tests on multiple browsers.

The functional tests have been broken down into Categories > Groups > Tests

- Each category has it's own folder within the selenium_tests directory, it contains multiple groups of tests
- Each group of tests gas it's own python file within the category folder, each group contains multiple tests

For general guidance on how to write the selenium tests, review the existing tests within this folder.


## Running tests locally

The tests are configured to run automatically through GitHub actions, although this may not be practicle during intial test development

The Selenium grid and webdriver is run from a docker container. Therefore to run tests locally you need to install docker desktop and have it running on your computer.

Then run the following commands
```
make selenium-up
```
This builds the docker containers required for testing

```
make selenium-local
```
This runs the tests themselves

You can view the tests as they run locally using a number of different methods, the options are explained at the link below
https://github.com/SeleniumHQ/docker-selenium#using-a-vnc-client