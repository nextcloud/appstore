#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2018 Nextcloud GmbH and Nextcloud contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

set -e

chown nextcloudappstore:nextcloudappstore -R /srv/logs
chown nextcloudappstore:nextcloudappstore -R /srv/media

# adjust database schema and load new data into it
python manage.py migrate
python manage.py loaddata nextcloudappstore/core/fixtures/*.json
python manage.py importdbtranslations

# copy data served by web server data into mounted volume
python manage.py collectstatic --noinput

exec "$@"
