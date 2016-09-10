# only random once obviously ;)
python=venv/bin/python
pip=venv/bin/pip
pycodestyle=venv/bin/pycodestyle
pyresttest=venv/bin/pyresttest
mypy=venv/bin/mypy
manage=$(python) $(CURDIR)/manage.py

.PHONY: lint
lint:
	$(pycodestyle) $(CURDIR)/nextcloudappstore --exclude=migrations
	$(mypy) --silent-imports --disallow-untyped-defs $(CURDIR)/nextcloudappstore/core/api/v1/release

.PHONY: test
test: lint
	$(manage) test --settings nextcloudappstore.settings.development

.PHONY: resetup
resetup:
	rm -f db.sqlite3
	$(manage) migrate --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; from allauth.account.models import EmailAddress; EmailAddress.objects.create(user=User.objects.get(username='admin'), email='admin@example.com', verified=True, primary=True)" | $(manage) shell --settings nextcloudappstore.settings.development
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.json --settings nextcloudappstore.settings.development

.PHONY: initmigrations
initmigrations:
	rm -f $(CURDIR)/nextcloudappstore/**/migrations/0*.py
	$(manage) makemigrations --settings nextcloudappstore.settings.development

# Only for local setup, do not use in production
.PHONY: dev-setup
dev-setup:
	pyvenv venv
	$(pip) install -r $(CURDIR)/requirements/development.txt
	$(pip) install -r $(CURDIR)/requirements/base.txt
	@echo "from nextcloudappstore.settings.base import *" > $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "DEBUG = True" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "SECRET_KEY = 'secret'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "RECAPTCHA_PUBLIC_KEY = '<RECAPTCHA_PUBLIC_KEY>'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "RECAPTCHA_PRIVATE_KEY = '<RECAPTCHA_PRIVATE_KEY>'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "EMAIL_HOST = 'localhost'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "DEFAULT_FROM_EMAIL = 'Appstore <appstore@nextcloud.com>'" >> $(CURDIR)/nextcloudappstore/settings/development.py
	@echo "INSTALLED_APPS.append('debug_toolbar')" >> $(CURDIR)/nextcloudappstore/settings/development.py
	$(manage) migrate --settings nextcloudappstore.settings.development
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.json --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; from allauth.account.models import EmailAddress; EmailAddress.objects.create(user=User.objects.get(username='admin'), email='admin@example.com', verified=True, primary=True)" | $(manage) shell --settings nextcloudappstore.settings.development

.PHONY: docs
docs:
	@echo "hi"
	$(MAKE) -C $(CURDIR)/docs/ html
