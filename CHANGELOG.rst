.. :changelog:

Changelog
---------

0.1.0 - 2016-10-xx
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
- Fix backlinks on app releases page


0.1.0 - 2016-09-21
++++++++++++++++++

**Added**

- First release
