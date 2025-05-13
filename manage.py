#!/usr/bin/env python
#
# SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nextcloudappstore.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
