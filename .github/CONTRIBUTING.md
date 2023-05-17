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
* We only support and recommend the latest browser versions of:
  - Chrome
  - Safari
  - Edge
  - Firefox
* __SECURITY__: Report any potential security bug to us by following our [security policy](https://nextcloud.com/security/) instead of filing an issue in our bug tracker.

* Report the issue using our [template][template], it includes all the information we need to track down the issue.

Help us to maximize the effort we can spend fixing issues and adding new features, by not reporting duplicate issues.

[template]: https://raw.githubusercontent.com/nextcloud/appstore/master/.github/issue_template.md
[forum]: https://help.nextcloud.com/
[irc]: https://webchat.freenode.net/?channels=nextcloud-dev

## Contributing to Source Code

Thanks for wanting to contribute source code to Nextcloud. That's great!

However before you start to work on an issue or new feature, make sure **that you file an issue first**. That way we can minimize the chance that your work is not accepted or lots of change requests are made. This will keep both parties happy and save time :)

The backend is written in Django while the frontend uses custom TypeScript code. If you are interested in using a frontend JavaScript framework, please file an issue. We currently tend towards [Angular](https://angular.io/).

If you need help in setting up a local App Store installation, consult the [documentation](http://nextcloudappstore.readthedocs.io/en/latest)

### Tests

When submitting a pull request, you should ensure that the functionality is covered by an acceptance, integration or unit test. We employ unit and integration testing for both frontend and backend code but we do not have a UX test suite yet (if you are interested in integrating one please open an issue!!!).

Use acceptance tests (selenium tests) when:

* the functionality is a bigger chunk of a use case, e.g. registering an app or searching and downloading a compatible app for a specific Nextcloud version
* the functionality is primarily exposed to a user

Use unit tests when:

* the functionality depends on little to no extra dependencies
* the functionality is [pure](https://en.wikipedia.org/wiki/Pure_function)

Use integration tests when:

* the functionality would require more than 2 mocks to unit test
* the functionality depends on a context (e.g. reading files, accessing APIs, saving and retrieving database values)

All test suites can be run with:

    make test

### Linting/Coding-Style

We use [pre-commit](https://pre-commit.com) hooks to analyze Python code. Install a pre-commit and after that run:

    pre-commit install

This will run linter checks every time you make a commit. Even if the changes are made to non-Python code, we recommend running these hooks.

Travis-CI also runs TSLint. You will have to install and run TSLint locally since we do not trust the company that develops it: the lib is developed by Palantir, a large American NSA/CIA contractor. If you do not want to do that you can run the linting on Travis-CI when creating a pull request.

If you are interested in adding a CSS lint tool, feel free to do so :)

### Sign your work

We use the Developer Certificate of Origin (DCO) as a additional safeguard
for the Nextcloud project. This is a well established and widely used
mechanism to assure contributors have confirmed their right to license
their contribution under the project's license.
Please read [the relevant documentation][dcofile].
If you can certify it, then just add a line to every git commit message:

````
  Signed-off-by: Random J Developer <random@developer.example.org>
````

Use your real name (sorry, no pseudonyms or anonymous contributions).
If you set your `user.name` and `user.email` git configs, you can sign your
commit automatically with `git commit -s`. You can also use git [aliases](https://git-scm.com/book/tr/v2/Git-Basics-Git-Aliases)
like `git config --global alias.ci 'commit -s'`. Now you can commit with
`git ci` and the commit will be signed.

[devmanual]: https://docs.nextcloud.org/server/12/developer_manual/
[dcofile]: https://github.com/nextcloud/server/blob/master/contribute/developer-certificate-of-origin

## Translations
Please submit translations via [Transifex][transifex].

[transifex]: https://www.transifex.com/nextcloud/nextcloud/appstore/
