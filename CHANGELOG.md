# Changelog

## [Unreleased] 

### Added

- Add games category

### Removed

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

- Better error message when database.xml validation fails

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
