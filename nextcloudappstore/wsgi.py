"""
WSGI config for nextcloudappstore project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
from os.path import abspath, dirname, isfile, join, pardir, realpath

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nextcloudappstore.settings.production")

application = get_wsgi_application()


def find_in_root(path):
    return join(realpath(join(dirname(abspath(__file__)), pardir)), path)


# if a new relic config file is present enable it
relic_conf = os.environ.get("NEWRELIC_PATH", find_in_root("newrelic.ini"))

if isfile(relic_conf):
    import newrelic.agent

    newrelic.agent.initialize(relic_conf)
    application = newrelic.agent.WSGIApplicationWrapper(application)
