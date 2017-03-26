Development
===========
The app store uses a Makefile for common tasks. The following useful Make commands are available:


make dev-setup
    installs a local development setup (requires previous setup, see :ref:`development-install`)

make test
    runs the frontend and backend test suite

make lint
    runs the code-style checker

make authors
    updates the AUTHORS.rst file based on the git database

make docs
    regenerates up to html date docs in docs/_build/html

make update-dev-deps
    updates your python, bower and npm dependencies

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

    npm install --upgrade

and then run::

    npm run build

If you are developing and wish to automatically compile on filechanges run::

    npm run watch

Testing
~~~~~~~

The unit and integration test suite is run by executing the following command::

    npm test

If you are developing and wish to automatically re-run your test suite on filechanges run::

    npm run watch-test
