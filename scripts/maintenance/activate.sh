#!/usr/bin/env bash
# Small script for activating the venv and exporting all the important env
# variables

set -e
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=nextcloudappstore.settings.production
export LANG=en_EN.UTF-8
