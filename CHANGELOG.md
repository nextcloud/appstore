# Changelog

## [Unreleased]

## [4.3.1]  - 2023-09-19

### Changed

- Replaced `psycopg2` with new `psycopg` package. #1143
- Updated dependencies & packages. #1129

## [4.3.0]  - 2023-09-07

### Changed

- Replaced `django-cors-middleware` package with `django-cors-headers`
- Updated Django from `3.2` to `4.2.5` version.

### Fixed

- Bug in REST API for deleting releases when APP_ID contains number. #1127

## [4.2.0]  - 2023-07-18

### Changed

- Dropped Python 3.7/3.8 support
- Updated dependencies & packages.

### Fixed

- Added default bruteforce login protection. #1087
- Added rate limit to `API token generating`. #1088
- Added `Password reset` rate limit configuration. #1077
- Forced user logout after 15 failed attempts to change password. #1078

## [4.1.0]  - 2023-05-18

### Added

- Notify users on password change

### Changed

- Updated Python and JavaScript dependencies
- Dropped Python 3.6 support

## [4.0.0]  - 2018-11-10

### Added

- Support for Nextcloud 14
- Add info.xml validation for fulltextsearch and dashboard

### Changed

- Updated Python and JavaScript dependencies
- Make test output more verbose
- Pin down Travis-CI versions to match Ubuntu 16.04

### Removed

- Removed Support for Nextcloud 11
- Removed compiled JavaScript files from version control

### Security

- Disable HMAC email validation so that an cooldown period is respected, #584

## [3.4.0]  - 2018-05-18

### Added

- Added search category

### Changed

- Add quicknotes to CRL
- Updated libraries

## [3.3.0]  - 2018-02-18

### Added

- Add support for generating apps for Nextcloud 13
- Add support for personal setting tags in info.xml and ids instead of URLs for documentation
- Add another flag to differentiate between supported and unreleased Nextcloud releases

## [3.2.0]  - 2018-02-04

### Added

- **syncnextcloudreleases** command to sync Nextcloud releases directly from GitHub

### Removed

- Nextcloud releases are not imported via fixtures anymore, use the **syncnextcloudreleases** command

### Security

- Narrow down fixtures to not accidentally import test data on production systems. Check if a user with the user name **admin** was created. If so delete that user from your system.

## [3.1.2] - 2018-02-02

### Security

- Update dependencies to latest Django security fix

### Fixed

- Correctly import settings for:
  - APP_SCAFFOLDING_PROFILES
  - DISCOURSE_URL
  - CERTIFICATE_DIGEST


## [3.1.1] - 2018-01-02

### Changed

- Get rid of moment.js and add functionality on the server in order to reduce file size
- Only load subset of languages for highlight.js


## [3.1.0] - 2018-01-01

### Added

- Fail if .git folders are shipped in the archive release, #537

### Changed

- Updated 3rdparty libraries

## [3.0.2] - 2017-11-16

### Security

- Require password when changing your account details
- Regenerate API token on password change

## [3.0.1] - 2017-11-15

### Security

- Require admin users to log in over the rate limited default login form

## [3.0.0] - 2017-11-15

### Security

- Log out user on password change to prevent hackers from retaining a stolen user session even after a new password was set, #532
- Reduce password reset link validity timespan from 3 to 1 day, #532

### Added

- Add games category
- Add a newest release feed for each app on their detail page, #496
- Add a createtestuser command for easily setting up users in development
- Automatically log in user on successful email confirmation, #400
- Added security category
- Added collaboration tag for info.xml, #521 and #524
- Added sabredav plugins for info.xml, #527
- Added docs on how to configure IntelliJ/PyCharm and commit project configuration files
- **API (v1)**: future proof signatures by adding a **signatureDigest** field to each app release filled with the hashing algorithm
- **API (v1)**: add **discussion** field to each app that links to its forum
- **API (v1)**: Add a new API route to fetch all Nextcloud releases

### Changed

- Bring back **discussion** tag in info.xml which allows you to define your own forum link. If absent, it will default to our forum at help.nextcloud.com
- Use one unique button style for all buttons, #402
- Moved certificate and scaffolding to separate folders
- Moved Nextcloud public certificate and CRL to new folder
- Trim text of most info.xml elements

### Removed

- Removed **auth** category, use **security** instead
- Dropped Node.js 7 support and require Node.js 8+
- Dropped support for Nextcloud 9 and 10:
  - owncloud tag in info.xml will not be migrated to nextcloud tags anymore
  - ocsid will not be parsed anymore and was removed from the info.xsd
  - old categories will not be migrated anymore (tool, game, productivity, other)
  - presence of owncloud tag will not be validated anymore for apps depending on 9 and 10
  - v0 API was removed
  - nextcloudrelease.json fixtures for 9 and 10 were removed
  - Nextcloud 10 apps can not be generated anymore

## Fixed

- Fixed an issue that would sometimes not import translated categories properly
- Better error message when database.xml validation fails
- Update travis configuration and fix test suite for generating Nextcloud 12 apps
- Treat and encode all scaffolding files as unicode and set the correct size, #522

## [2.0.0] - 2017-06-02

### Security

- Validate certificate signatures before letting people register public certificates. This would only allow developers to claim apps if they knew the public certificate. App uploads however were impossible without knowing the signature.

### Added

- Lazy-load images in app list
- Added new Nextcloud version fixtures
- Added support for several new XML elements in schema
- Added support to switch between language comments
- Added support to easily post ratings in multiple languages
- Added support for running New Relic on servers
- Added ability to transfer app ownership
- Added commands to update tokens, set a default password for an admin user for development and verify an email address
- Added Nextcloud 12 app template
- Added validation for database.xml files
- Added support for Apache 2.0 and MPL 2.0 licenses

### Fixed

- Replace _ with - in app ids to match Discourse links
- Remove duplicate entries for languages in comments
- Fix layout issues in list view if app names were longer than expected
- Return proper 400 codes in case certificate validation fails
- API: Do not return duplicate releases for apps
- Do not show an error message when an unexpected content type is being returned when registering or uploading an app

### Changed

- Migrated frontend code to Typescript + Webpack
- Require bug tracker to present in info.xml
- Require max-version to be present for Nextcloud versions
- Extracted api and account settings into a separate app
- Moved app schema to a different path, make sure to adjust your web-server config
- Migrated to yarn as package manager
- The update script now stops and restarts the apache server during the update
- MAX_DOWNLOAD_INFO_XML_SIZE setting has been renamed to MAX_DOWNLOAD_FILE_SIZE which defaults to 1Mb now instead of 512Kbs
- Another schema (database.xsd) needs to be added to your web-server config

### Removed

- Dropped Python 3.4 support
- Dropped app ownership table

## [1.0.0] - 2016-13-12

### Added

- Add ability to add nightlies and pre-releases to app release feed by appending ?prerelease=true&nightly=true to feed url
- Add changelog to app release feed
- Add number of recent and overall ratings to API
- Add app development templates for Nextcloud 10
- Add a way for developers to define a smaller thumbnail for a screenshot and expose it in the API

### Changed

- Information related to the app and not the app release should only be updated when stable, new releases are uploaded
- Manage Nextcloud releases in the admin interface instead of a Python file
- Apps need to provide a maximum version in addition to the minimum version
- Apps do not need to provide an owncloud tag anymore for Nextcloud 11
- RSS and Atom feed links now redirect to the app store app detail page instead of the download link. The download link is now available at the bottom of the entry

### Removed

- Remove nightlies and pre-releases from app release feed

### Fixed

- Apps depending on Nextcloud minor or patch versions are now rendered on the app detail and releases page
- Fix styling bug that would sometimes hide the app resource links when in mobile mode
- Allow digits in app id, #370
- Do not expose incompatible app releases in REST API


## [0.2.0] - 2016-10-23

### Added

- Faster API E-Tag generation
- Faster API and web interface due to reduced sql queries
- Generate apps through the web interface
- Add validation for command tags in info.xml
- Parse appid/CHANGELOG.md if present following the keep a changelog format
- Add legacy API so Nextcloud 9 and 10 can switch to the new store
- Allow semver pre-releases, e.g. 1.0.0-alpha
- Featured flags are now exposed in the API

### Changed

- Improve admin interface
- Change some urls to prevent clashes with app names
- Combine app developer related tasks in one drop-down-menu
- Hide app rating form from app owner
- Naming and usability fixes for app rating form
- Boolean fields are now prefixed with **is** in the API
- API route for deleting releases is now split up into two routes: one for normal and one for nightly releases

### Fixed

- Fixed syntax highlighting for Markdown
- Fixed regex for commands
- Fixed back-links on app releases page

### Removed

- Removed discussion info.xml tag, instead link to the discourse forum app category and create categories in the forum when registering apps

## [0.1.0] - 2016-09-21

### Added

- First release
