# SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"
DATABASES["default"]["NAME"] = "nextcloudappstore"
DATABASES["default"]["USER"] = "postgres"
DATABASES["default"]["PASSWORD"] = "postgres"
DATABASES["default"]["PORT"] = "5432"
DATABASES["default"]["HOST"] = "127.0.0.1"
