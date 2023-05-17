import sys

if "test" in sys.argv:
    DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3"}
