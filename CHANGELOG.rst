.. :changelog:

Changelog
---------

1.0.0 - 2016-13-12
++++++++++++++++++

**Added**

- Add ability to add nightlies and pre-releases to app release feed by appending ?prerelease=true&nightly=true to feed url
- Add changelog to app release feed
- Add number of recent and overall ratings to API
- Add app development templates for Nextcloud 10
- Add a way for developers to define a smaller thumbnail for a screenshot and expose it in the API

**Changed**

- Information related to the app and not the app release should only be updated when stable, new releases are uploaded
- Manage Nextcloud releases in the admin interface instead of a Python file
- Apps need to provide a maximum version in addition to the minimum version
- Apps do not need to provide an owncloud tag anymore for Nextcloud 11
- RSS and Atom feed links now redirect to the app store app detail page instead of the download link. The download link is now available at the bottom of the entry

**Removed**

- Remove nightlies and pre-releases from app release feed

**Fixed**

- Apps depending on Nextcloud minor or patch versions are now rendered on the app detail and releases page
- Fix styling bug that would sometimes hide the app resource links when in mobile mode
- Allow digits in app id, #370
- Do not expose incompatible app releases in REST API


0.2.0 - 2016-10-23
++++++++++++++++++

**Added**

- Faster API E-Tag generation
- Faster API and web interface due to reduced sql queries
- Generate apps through the web interface
- Add validation for command tags in info.xml
- Parse appid/CHANGELOG.md if present following the keep a changelog format
- Add legacy API so Nextcloud 9 and 10 can switch to the new store
- Allow semver pre-releases, e.g. 1.0.0-alpha
- Featured flags are now exposed in the API

**Changed**

- Improve admin interface
- Change some urls to prevent clashes with app names
- Combine app developer related tasks in one dropdown-menu
- Hide app rating form from app owner
- Naming and usability fixes for app rating form
- Boolean fields are now prefixed with **is** in the API
- API route for deleting releases is now split up into two routes: one for normal and one for nightly releases

**Fixed**

- Fixed syntax highlightning for Markdown
- Fixed regex for commands
- Fixed backlinks on app releases page

**Removed**

- Removed discussion info.xml tag, instead link to the discourse forum app category and create categories in the forum when registering apps

0.1.0 - 2016-09-21
++++++++++++++++++

**Added**

- First release
