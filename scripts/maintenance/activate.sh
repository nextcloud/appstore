#!/usr/bin/env bash
# Small script for activating the venv and exporting all the important env
# variables. Execute it by using
#
# source scripts/maintenance/activate.sh

source venv/bin/activate
export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production
export LANG=en_EN.UTF-8
