#!/usr/bin/env bash
# File has to be run from inside your top level cloned folder, e.g.
#
#     bash scripts/maintenance/update.sh apache
#
# The script has to have rights to write into the current directory and into
# the web server folder.
#
# The venv folder needs to be in the same top level directory
# The first argument to the script is the web server, currently only apache is
# supported

set -e

if [[ "$1" == "apache" ]]; then
    reload_cmd="systemctl reload apache2"
else
    echo "No known web server configuration for argument '$1', aborting"
    exit 1
fi

source venv/bin/activate
export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production
export LANG=en_EN.UTF-8
pip install --upgrade wheel
pip install --upgrade pip
pip install --upgrade -r requirements/base.txt
pip install --upgrade -r requirements/production.txt
python manage.py migrate
python manage.py loaddata nextcloudappstore/**/fixtures/*.json
python manage.py collectstatic
eval $reload_cmd
deactivate
