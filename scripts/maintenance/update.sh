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
    stop_cmd="systemctl stop apache2"
    start_cmd="systemctl start apache2"
else
    echo "No known web server configuration for argument '$1', aborting"
    exit 1
fi

# Fix locales
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"

# get rid of old tmp venv if present and create a new tmp venv
rm -rf venvtmp/
python3 -m venv venvtmp

# shut down for maintenance
eval $stop_cmd
source venvtmp/bin/activate

export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production
export LANG=en_EN.UTF-8
poetry install
npm ci
npm run build
python manage.py migrate
python manage.py loaddata nextcloudappstore/core/fixtures/*.json
python manage.py collectstatic --noinput
python manage.py compilemessages
python manage.py importdbtranslations

deactivate

# get rid of old venv if it exists and move the tmp venv into place
if [[ -d "venv" ]]; then
    mv venv venvold
fi
mv venvtmp venv

eval $start_cmd

rm -rf venvold
