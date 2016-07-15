# only random once obviously ;)
python=venv/bin/python
pip=pip3
pycodestyle=venv/bin/pycodestyle
pyresttest=venv/bin/pyresttest
mypy=venv/bin/mypy
manage=$(python) $(CURDIR)/manage.py

lint:
	$(pycodestyle) $(CURDIR)/nextcloudappstore --exclude=migrations
	$(mypy) --silent-imports --disallow-untyped-defs $(CURDIR)/nextcloudappstore/core/api/v1/release

test: lint
	$(manage) test --settings nextcloudappstore.settings.development

resetup:
	rm -f db.sqlite3
	$(manage) migrate --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; from allauth.account.models import EmailAddress; EmailAddress.objects.create(user=User.objects.get(username='admin'), email='admin@example.com', verified=True, primary=True)" | $(manage) shell --settings nextcloudappstore.settings.development
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.json --settings nextcloudappstore.settings.development

initmigrations:
	rm -f $(CURDIR)/nextcloudappstore/**/migrations/0*.py
	$(manage) makemigrations --settings nextcloudappstore.settings.development

# Only for local setup, do not use in production
dev-setup:
	pyvenv venv --system-site-packages
	ls -la venv
	ls -la venv/bin
	$(pip) install -r $(CURDIR)/requirements/development.txt
	$(pip) install -r $(CURDIR)/requirements/base.txt
	@echo "from nextcloudappstore.settings.base import *" > $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "DEBUG = True" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "SECRET_KEY = 'secret'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "RECAPTCHA_PUBLIC_KEY = '<RECAPTCHA_PUBLIC_KEY>'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "RECAPTCHA_PRIVATE_KEY = '<RECAPTCHA_PRIVATE_KEY>'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "EMAIL_HOST = 'localhost'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "DEFAULT_FROM_EMAIL = 'Appstore <appstore@nextcloud.com>'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "INSTALLED_APPS.append('debug_toolbar')" >> $(CURDIR)/nextcloudappstore/settings/development.py
	$(manage) migrate --settings nextcloudappstore.settings.development
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.json --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; from allauth.account.models import EmailAddress; EmailAddress.objects.create(user=User.objects.get(username='admin'), email='admin@example.com', verified=True, primary=True)" | $(manage) shell --settings nextcloudappstore.settings.development
