## Submitting issues

If you have questions about how to install or use the App Store, please direct these to our [forum][forum]. We are also available on [IRC][irc].

### Short version

 * The [**issue template can be found here**][template]. Please always use the issue template when reporting issues.

### Guidelines
* Please search the existing issues first, it's likely that your issue was already reported or even fixed.
  - Go to one of the repositories, click "issues" and type any word in the top search/command bar.
  - You can also filter by appending e. g. "state:open" to the search string.
  - More info on [search syntax within github](https://help.github.com/articles/searching-issues)
* This repository ([appstore](https://github.com/nextcloud/appstore/issues)) is *only* for issues for the Nextcloud App Store at [https://apps.nextcloud.com](https://apps.nextcloud.com) and not for app store functionality in your Nextcloud server.
* __SECURITY__: Report any potential security bug to us by following our [security policy](https://nextcloud.com/security/) instead of filing an issue in our bug tracker.

* Report the issue using our [template][template], it includes all the information we need to track down the issue.

Help us to maximize the effort we can spend fixing issues and adding new features, by not reporting duplicate issues.

[template]: https://raw.githubusercontent.com/nextcloud/appstore/master/.github/issue_template.md
[forum]: https://help.nextcloud.com/
[irc]: https://webchat.freenode.net/?channels=nextcloud-dev

## Contributing to Source Code

Thanks for wanting to contribute source code to Nextcloud. That's great!

### Tests

When submitting a pull request, you should ensure that the functionality is covered by an integration or unit test. We employ unit and integration testing for both frontend and backend code but we do not have a UX test suite yet (if you are interested in integrating one please open an issue!!!).

Use unit tests when:

* the functionality depends on little to no extra dependencies
* the functionality is [pure](https://en.wikipedia.org/wiki/Pure_function)

Use integration tests when:

* the functionality would require more than 2 mocks to unit test
* the functionality depends on a context (e.g. reading files, accessing APIs, saving and retrieving database values)

All test suites can be run with:

    make test

### Sign your work

We use the Developer Certificate of Origin (DCO) as a additional safeguard
for the Nextcloud project. This is a well established and widely used
mechanism to assure contributors have confirmed their right to license
their contribution under the project's license.
Please read [contribute/developer-certificate-of-origin][dcofile].
If you can certify it, then just add a line to every git commit message:

````
  Signed-off-by: Random J Developer <random@developer.example.org>
````

Use your real name (sorry, no pseudonyms or anonymous contributions).
If you set your `user.name` and `user.email` git configs, you can sign your
commit automatically with `git commit -s`. You can also use git [aliases](https://git-scm.com/book/tr/v2/Git-Basics-Git-Aliases)
like `git config --global alias.ci 'commit -s'`. Now you can commit with
`git ci` and the commit will be signed.

### Apply a license

In case you are not sure how to add or update the license header correctly please have a look at [the documentation][applyalicense]

[devmanual]: https://docs.nextcloud.org/server/12/developer_manual/
[dcofile]: https://github.com/nextcloud/server/blob/master/contribute/developer-certificate-of-origin
[applyalicense]: https://github.com/nextcloud/server/blob/master/contribute/HowToApplyALicense.md

## Translations
Please submit translations via [Transifex][transifex].

[transifex]: https://www.transifex.com/nextcloud
