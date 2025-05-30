<!--
  - SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
  - SPDX-License-Identifier: AGPL-3.0-or-later
-->
# Changelog

## [Unreleased]

## [4.10.0]  - 2024-05-30

### Added

- REUSE compliance. #1603 #1604 #1607 #1608 #1614
- AI category. #1594 #1596
- SPDX identifiers for currently supported licenses as `licence` XML values
  (for apps targeting Nextcloud versions 31 or later). #1560
- Note marking bundled apps as shipped. #1561
- Check if app is in hardcoded bundled list. #1558
- Odoo integration (newsletter mailing list). #1518 #1523 #1524 #1525 #1527
- Search by app ID. #1469
- Cache for `60 sec` for `latest_releases_by_platform_v` method. #1468

### Changed

- Use default password reset form from allauth. #1613
- Allow `scopes` be not present in `external-app`. #1497
- Default `discussion` URLs for apps. #1496
- Update dashboard icon. #1461
- Multiple dependency updates. #1340 #1364 #1366 #1427 #1429 #1435 #1436 #1439
  #1442 #1463 #1476 #1477 #1478 #1480 #1481 #1491 #1520 #1522 #1530 #1531 #1532
  #1537 #1539 #1545 #1546 #1548 #1551 #1564 #1567 #1573 #1576 #1578 #1600
- Multiple documentation updates. #1457 #1612

### Fixed

- Wrap XML values containing escape characters in CDATA sections. #1618
- Password reset from email token success page style. #1617
- Top navigation bar layout for large viewport width. #1611
- Clear browser cache for user account pages after logout. #1572
- Send confirmation email for and verify updated email addresses. #1571
- Validation for "Download link (tar.gz)" field. #1562
- Typo in app name hint. #1517
- Unstable version handling. #1515
- Donation type and attribute. #1487 #1492
- Consider "integrations" always up to date. #1470
- Optimized viewing of app store pages. #1467
- Broken doc links. #1459

## [4.9.0]  - 2024-08-19

### Added

- `donation` XML attribute and donation button display for apps. #1452
- Option to add enterprise support request button to apps. #1449
- Link to documentation for monetization features. #1453
- Relevance sorting option. #1426
- Ability to mark apps as orphaned/unmaintained. #1421
- Warning banner for apps without a release on recent Nextcloud versions. #1419

### Changed

- Multiple dependency updates. #1379 #1386 #1382 #1388 #1389 #1390 #1391 #1392
  #1393 #1400 #1401 #1404 #1409 #1412 #1414 #1415 #1417 #1428 #1430 #1431 #1433
  #1438 #1448

### Fixed

- Escape characters in translation string. #1425 #1441
- Adjust banner height on medium browser width. #1423
- Cleanup Makefile variables. #1367

## [4.8.1]  - 2024-05-10

### Changed

- `App templates` now generated from GitHub repo template. #1368 by @provokateurin
- redis dependency updated from `5.0.3` to `5.0.4` #1363
- sqlparse dependency updated from `0.4.4` to `0.5.0` #1353
- dnspython dependency updated from `2.5.0` to `2.6.1` #1351
- pillow dependency updated from `10.2.0` to `10.3.0` #1346

## [4.8.0]  - 2024-03-17

### Added

- App-discover API endpoint for `Nextcloud 29` #1302 #1313

### Changed

- follow-redirects updated from `1.15.5` to `1.15.6` #1315
- jasmine-core updated from `5.1.1` to `5.1.2` #1309
- karma updated from `6.4.2` to `6.4.3` #1310
- karma-webpack updated from `5.0.0` to `5.0.1` #1318

### Fixed

- Broken templates after `django-allauth` update. #1304
- Documentation hosting & building.

## [4.7.0]  - 2024-02-15

### Added

- Email validation during account registration. #1299

### Changed

- AppAPI: removed `protocol` and reworked `scopes` in `info.xml`. #1288
- django updated from `4.2.8` to `4.2.9` #1268 #1295
- jinja2 updated from `3.1.2` to `3.1.3` #1278
- pillow updated from `10.0.1` to `10.2.0` #1283
- follow-redirects updated from `1.15.2` to `1.15.5` #1286

## [4.6.0]  - 2024-01-02

### Added

- Ability to mark comments as a spam for an admin review. #1256

### Changed

- lxml updated from `4.9.3` to `4.9.4`

## [4.5.0]  - 2023-12-21

### Added

- Podcasts. #1202 @andrey18106

### Changed

- New UI. #1202 by @andrey18106 and @szaimen
- urllib3 updated from `2.0.6` to `2.0.7`
- django updated from `4.2.5` to `4.2.8`
- django-simple-captcha updated from `0.5.18` to `0.5.20`
- django-cors-headers updated from `4.2.0` to `4.3.1`
- psycopg updated from `3.1.13` to `3.1.14`
- markdown updated to `3.5.1`
- Updated NPM dependencies.

### Fixed

- App templates updated. #1234 by @kesselb
- Allow `ExApp` without API scopes.
- Allow uploading of GPLv3 licensed application releases.

## [4.4.1]  - 2023-10-05

### Changed

- Dropped Python 3.9 support. #1163

### Fixed

- Allow uploading of MIT licensed application releases. #1165
- Adjusted Makefile in the app generation template. #1166

## [4.4.0]  - 2023-10-03

### Added

- AppAPI applications upload & download support. #1145

### Changed

- **Node.js:** Now requires `v20` or higher.
- **npm:** Now requires `v9` or higher.
- Updated python dependencies.
- Updated `highlight.js` dependency to last major version. #1063
- Updated `django-allauth` from 0.54 to 0.57. #1152

## [4.3.2]  - 2023-09-23

### Added

- Support of `Last-Modified`, e.g. `If-Modified-Since:` header for the Rest API endpoints. #1147
- `redis` python dependency for `django-allauth`.

### Changed

- `/api/v1/apps.json` endpoint now ALWAYS return gzipped data. #1147

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
