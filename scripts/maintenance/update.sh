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

# Fix locales
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"

# get rid of old venv if present and create a new venv
rm -rf venvtmp/
python3 -m venv venvtmp
source venvtmp/bin/activate

export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production
export LANG=en_EN.UTF-8
pip install --upgrade wheel
pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/production.txt
python manage.py migrate
python manage.py loaddata nextcloudappstore/**/fixtures/*.json
python manage.py collectstatic
python manage.py compilemessages
python manage.py importdbtranslations
yarn install
yarn run build

deactivate

# get rid of old venv if it exists
if [[ -d "venv" ]]; then
    mv venv venvold
fi

mv venvtmp venv

eval $reload_cmd

rm -rf venvold
