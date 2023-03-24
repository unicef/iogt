# Current process

 1. Ensure all automated tests are passing
 2. Freeze the `develop` branch - only release hardening allowed
 3. Create a draft release in Github
 4. Set `SITE_VERSION` in [production settings][1] to the next release version; commit to develop
 5. Build a Docker container image based on latest `develop` branch
 6. Deploy the container image in a pre-production environment
 7. Perform manual QA
 8. Fix bugs, if any, then go back to step 5 and repeat until all bugs are gone
 9. Publish the draft release in Github -  this will tag the develop branch with the next release version

# Version numbers

## General

This project follows [semantic versioning][2].

There is no plan to increment the major version, for the foreseeable future. This means:

- Only the minor and patch versions should be considered when incrementing.
- All new functionality must to be added in a backwards compatible manner.

## Release candidates

Release candidates follow the [pre-release version notation][3] of semantic versioning, with a project-specific convention. All release candidate version numbers consist of the normal version number followed by a hyphen, then the characters 'rc' (for release candidate), a dot, then the number of the release candidate. For example, the first candidate for release 2.3.3 would be '2.3.3-rc.1'. If bugs are found and fixed, resulting in a second candidate the version number would be '2.3.3-rc.2', and so on.


[1]: ../iogt/settings/production.py
[2]: https://semver.org/
[3]: https://semver.org/#spec-item-9
