news (9.0.4)
* **Bugfix**: Pad API last modified timestamp to milliseconds in updated items API to return only new items. API users however need to re-sync their complete contents, #24
* **Bugfix**: Do not pad milliseconds for non millisecond timestamps in API

news (9.0.3)
* **Security (Low)**: Prevent browsers like Chrome from auto-filling your Nextcloud login credentials into Basic Auth form. This could lead users to accidentally saving their credentials in the database and disclosing them to the feed source when the feed is added/updated

news (9.0.2)
* **Bugfix**: Do not return millisecond lastModified timestamps in API, #20

news (9.0.1)
* **Enhancement**: Drop PHP 64bit requirement due to helpful suggestions

news (9.0.0)
* **New dependency**: Bump minimum Nextcloud version to 10
* **New dependency**: PHP 64bit required
* **Backwards incompatible change**: Updating to 9.0.0 is only possible from 8.8.0 or higher due complex database schema changes.
* **Enhancement**: Further cleanups for the Nextcloud app store
* **Bugfix**: Fix cronjob updates on Nextcloud 10
* **Bugfix**: Limit iframes to 100% width, #10

news (8.8.3)
* **Enhancement**: Cleanups for the Nextcloud app store

news (8.8.0)
* **Enhancement**: Remove current pull to refresh implementation since it is more annoying than helpful.
* **Enhancement**: Add API route for supported API levels

news (8.7.5)
* **Security (High)**: Fix security bug that would allow websites to access your DOM document when using keyboard shortcuts to open an article in a new tab, downloading audio files, opening links on the explore page or opening links to the ownCloud documentation or issue tracker (News app versions prior to 5.0.0 are also vulnerable when clicking on any link in the title or article body). This gives any attacker access to all data on the DOM and allows them to make arbitrary requests to the ownCloud server on the user's behalf, bypassing CSRF protection and gaining full access to their account by stealing their login cookies. For a more detailed explanation [visit this website](https://medium.com/@jitbit/target-blank-the-most-underestimated-vulnerability-ever-96e328301f4c#.h55ny7ef0)

news (8.7.4)
* **Bugfix**: Fix expand in compact view mode, #988

news (8.7.3)
* **Bugfix**: Rerun fingerprint and search index generation in case it was not run properly before
* **Bugfix**: Do not swallow errors when generating search indices and fingerprints

news (8.7.2)
* **Security**: Sign application to make missing/outdated files more easily detectable and prevent attackers from potentially serving a malicious News app from the app store

news (8.7.1)
* **Bugfix**: Send Chrome's user agent string instead of our own since mod_security, which is used on some servers, thinks that only browsers are allowed to send user agents. This will fix feed updates for some websites, e.g. joomla.org, (because we all know that Joomla is big on security ;) ), #978

news (8.7.0)
* **Enhancement**: Better lock down Composer versions to prevent shipping newer PHP libraries then intended when compiling the project
* **Enhancement**: Mark current article as active while scrolling
* **Enhancement**: Clicking on an article sets it as active, #791
* **Enhancement**: Keyboard shortcuts will target the currently active element, #791

news (8.6.0)
* **Enhancement**: Also publish error count and last error message through API, #977

news (8.5.0)
* **Bugfix**: Do not run feed updates when ajax or web cron mode was detected because it can lead to very long load times, timeouts, data corruption, update bugs where feeds are not updated anymore and database inconsistencies. If someone is interested in re-enabling webcron based feed updates, please create a PHP script which uses the [updater API](https://github.com/owncloud/news/wiki/Updater-1.2). Don't hesitate to ask for help on the issue tracker!
* **Bugfix**: Fix multiple error messages and outdated links for cron error messages

news (8.4.1)
* **Bugfix**: Fix error messages in the logs which were caused by outdated template includes, #972

news (0.103)
* Fixed a bug that prevented deleting feeds when a folder was deleted

news (0.102)
* Fix marking read of all articles and folders on mysql and postgres
* Fix bug that would still show items after its feed or folder has been marked as deleted
* Fix bug that would show invalid unread count for feeds whose folders were deleted

news (0.101)

* show 99+ as max unread count
* only show delete button if feed is active
* Fix a bug that would show the loading sign when updating the web ui and would reload all items while reading
* More accurate padding when hovering over a feed
* Require 5.0.6 which includes a fix for the core API
* Don't highlight the tab title when there are no new unread feeds
* Make only one http request for reading all items and all items of a folder
* Fix bug that would prevent marking a feed as read when its created and no other feeds are there
* Fix bug that would prevent readding of a feed when a folder containing the feed was deleted
* Also send newest item id in the api when creating a feed
* Fix a bug that would mark the items on the right side as read regardless of feed or folder id
* Fix a bug that would a feed from being added when he was deleted and then another feed was deleted
* When a feed is deleted and not undone in 10 seconds and the window is closed, delete him
* Fix bug that would make links containing hashes unclickable
* Fix bug that broke the News app on postgresql
* Fix bug that prevented the API from serving items

news (0.98)

* Fix XSS vulnerability in sanitation for json import
* Fix XSS vulnerability in feed and title link

news (0.97)

* Fix XSS vulnerability in sanitation
* Properly show embedded vimeo and youtube videos

news (0.96)

* Always open links in new tabs
* Better exception handling for controllers
* Implemented API
* Fixed a bug that would prevent update of the News app
* Log feed update errors
* Make add website button less obstrusive
* Fixed problem with sites that updated too frequently like youtube
* Also update folders

news (0.95)

* Fix a bug that would cause PHP 5.3 to fail while parsing utf-8
* Reverted the keep unread checkbox styling from a button back to a normal checkbox
* Fix an issue that prevented scrolling when drag and dropping a feed in to a new folder
* Do not mark items as read that have not yet been displayed to the user
* Autopage if there are 10 items left instead of 4 times the scroll area height, fixes a bug that would not load new items if the entry was too big
* Prefer website favicon over channel image, fixes wordpress blog favicons
* Add all businesslayer methods for the current API spec
* API Specification Draft
* Fix a bug that would cause words in the headlines to always be wrapped
* Fix a bug that would cause the ellipsis on the "Add Website" entry to be too short
* Provide undo dialog for feed and folder deletion
* Do not preload audio in podcast feed
* Use utf-8 charset header in JSON responses to prevent broken headlines
* Move the rss cache files into the ownCloud data directory
* Autopurge: limit read articles per feed instead of using a global limit
* Use tooltips for delete and mark read button
* Also load the newest unread and starred count when a feed is loaded
* Do not request updates from the client but only use the background job to make the app faster
* Add a way to import articles from Google Reader Takeout Archive
* Fix a bug in favicon fetcher that would not fetch certain favicons
* Add OPML export
* Show translated relative dates for articles
* Show immediate feedback when adding a feed or folder
* Add keyboard shortcuts
* Do not show unread articles feed when there are no feeds
* Filter HTML tags from headlines and authors
* If the article author has no name use the mail
* Show full feed name on hover
* If feed has no name, use its URL
* Do not update articles all the time that have no pubdate
* Prevent app from making ownCloud unusable if the App Framework is not installed
* Focus the articles area when a feed is being clicked so page up/page down work
* Use a delay for drag and drop to make experience on Mac OS X better
* Show unread count in the tab title
