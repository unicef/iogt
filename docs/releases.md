# Current process

 1. Ensure all automated tests are passing
 2. Freeze the `develop` branch - only release hardening allowed
 3. Create a draft release in Github
 4. Build a Docker container image based on latest `develop` branch
 5. Deploy the container image in a pre-production environment
 6. Perform manual QA
 7. Fix bugs, if any, then go back to step 5 and repeat until all bugs are gone
 8. Set `SITE_VERSION` in [production settings][1] to the next release version; commit to develop
 9. Publish the draft release in Github -  this will tag the develop branch with the next release version

# Version numbers

This project follows [semantic versioning][2].

There is no plan to increment the major version, for the foreseeable future. This means:

- Only the minor and patch versions should be considered when incrementing.
- All new functionality must to be added in a backwards compatible manner.


[1]: ../iogt/settings/production.py
[2]: https://semver.org/
