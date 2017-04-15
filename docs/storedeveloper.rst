Development
===========
The app store uses a Makefile for common tasks. The following useful Make commands are available:


make dev-setup
    installs a local development setup (requires previous setup, see :doc:`devinstall`)

make test
    runs the frontend and backend test suite

make lint
    runs the code-style checker

make authors
    updates the AUTHORS.rst file based on the git database

make docs
    regenerates up to html date docs in docs/_build/html

make update-dev-deps
    updates your python, bower and yarn dependencies

make resetup
    kills the current sqlite database and creates a new one

make test-data
    downloads and sets up test apps, needs certificate validation to be disabled and a running server at http://127.0.0.1:8000

make l10n
    compiles and installs translations

Frontend
--------

The frontend is written in TypeScript and compiles to ES6 using Webpack.

To run the frontend build make sure that all your deps are up to date::

    yarn install

and then run::

    yarn run build

If you are developing and wish to automatically compile on filechanges run::

    yarn run watch

Testing
~~~~~~~

The unit and integration test suite is run by executing the following command::

    yarn test

If you are developing and wish to automatically re-run your test suite on filechanges run::

    yarn run watch-test
