python=venv/bin/python
pip=venv/bin/pip
pycodestyle=venv/bin/pycodestyle
pyresttest=venv/bin/pyresttest
mypy=venv/bin/mypy
manage=$(python) $(CURDIR)/manage.py
db=sqlite
pyvenv=python3 -m venv
npm=npm
tslint=node_modules/.bin/tslint

.PHONY: lint
lint:
	$(tslint) "$(CURDIR)/nextcloudappstore/core/static/assets/**/*.ts"
	$(pycodestyle) $(CURDIR)/nextcloudappstore --exclude=migrations
	$(mypy) --silent-imports --disallow-untyped-defs $(CURDIR)/nextcloudappstore/core/api/v1/release
	$(mypy) --silent-imports --disallow-untyped-defs $(CURDIR)/nextcloudappstore/core/certificate

.PHONY: test
test: lint
	$(npm) test
	$(manage) test --settings nextcloudappstore.settings.development

.PHONY: resetup
resetup:
	rm -f db.sqlite3
	$(MAKE) initdb

.PHONY: initmigrations
initmigrations:
	rm -f $(CURDIR)/nextcloudappstore/**/migrations/0*.py
	$(manage) makemigrations --settings nextcloudappstore.settings.development

# Only for local setup, do not use in production
.PHONY: dev-setup
dev-setup:
	$(npm) install
	$(npm) run build
	$(pyvenv) venv
	$(pip) install --upgrade pip
	$(pip) install -r $(CURDIR)/requirements/development.txt
	$(pip) install -r $(CURDIR)/requirements/base.txt
ifeq ($(db), postgres)
	$(pip) install -r $(CURDIR)/requirements/production.txt
endif
	cp $(CURDIR)/scripts/development/settings/base.py $(CURDIR)/nextcloudappstore/settings/development.py
	cat $(CURDIR)/scripts/development/settings/$(db).py >> $(CURDIR)/nextcloudappstore/settings/development.py
	$(MAKE) initdb


.PHONY: initdb
initdb:
	$(manage) migrate --settings nextcloudappstore.settings.development
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.json --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell --settings nextcloudappstore.settings.development
	@echo "from django.contrib.auth.models import User; from allauth.account.models import EmailAddress; EmailAddress.objects.create(user=User.objects.get(username='admin'), email='admin@example.com', verified=True, primary=True)" | $(manage) shell --settings nextcloudappstore.settings.development

.PHONY: docs
docs:
	$(MAKE) -C $(CURDIR)/docs/ clean html

.PHONY: update-dev-deps
update-dev-deps:
	$(pip) install --upgrade -r $(CURDIR)/requirements/development.txt
	$(pip) install --upgrade -r $(CURDIR)/requirements/base.txt
	$(npm) install --upgrade

.PHONY: authors
authors:
	$(python) $(CURDIR)/scripts/generate_authors.py

.PHONY: clean
clean:
	rm -rf $(CURDIR)/nextcloudappstore/core/static/vendor
	rm -rf $(CURDIR)/nextcloudappstore/core/static/public
	rm -rf $(CURDIR)/node_modules
	$(MAKE) -C $(CURDIR)/docs/ clean

