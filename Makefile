python=venv/bin/python
pip=venv/bin/pip
pycodestyle=venv/bin/pycodestyle
pyresttest=venv/bin/pyresttest
bandit=venv/bin/bandit
mypy=venv/bin/mypy
manage=$(python) $(CURDIR)/manage.py
db=sqlite
pyvenv=python3 -m venv
yarn=yarn

.PHONY: lint
lint:
	$(pycodestyle) $(CURDIR)/nextcloudappstore --exclude=migrations
	$(mypy) --silent-imports --disallow-untyped-defs $(CURDIR)/nextcloudappstore/api/v1/release
	$(mypy) --silent-imports --disallow-untyped-defs $(CURDIR)/nextcloudappstore/core/certificate
	$(bandit) -r $(CURDIR)/nextcloudappstore -c $(CURDIR)/.bandit.yml

.PHONY: test
test: lint
	$(yarn) test
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
	$(yarn) install
	$(yarn) run build
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
	$(manage) createsuperuser --username admin --email admin@admin.com --noinput --settings nextcloudappstore.settings.development
	$(manage) verifyemail --username admin --email admin@admin.com --settings nextcloudappstore.settings.development
	$(manage) setdefaultadminpassword --settings nextcloudappstore.settings.development

.PHONY: docs
docs:
	$(MAKE) -C $(CURDIR)/docs/ clean html

.PHONY: update-dev-deps
update-dev-deps:
	$(pip) install --upgrade -r $(CURDIR)/requirements/development.txt
	$(pip) install --upgrade -r $(CURDIR)/requirements/base.txt
	$(yarn) install --upgrade

.PHONY: authors
authors:
	$(python) $(CURDIR)/scripts/generate_authors.py

.PHONY: clean
clean:
	rm -rf $(CURDIR)/nextcloudappstore/core/static/vendor
	rm -rf $(CURDIR)/nextcloudappstore/core/static/public
	rm -rf $(CURDIR)/node_modules
	$(MAKE) -C $(CURDIR)/docs/ clean

.PHONE: test-data
test-data:
	$(manage) createtestuser --username user1 --password user1 --email user1@user.com --settings nextcloudappstore.settings.development
	$(manage) createtestuser --username user2 --password user2 --email user2@user.com --settings nextcloudappstore.settings.development
	$(manage) createtestuser --username user3 --password user3 --email user3@user.com --settings nextcloudappstore.settings.development
	$(python) $(CURDIR)/scripts/development/testdata.py

.PHONE: l10n
l10n:
	$(manage) compilemessages --settings nextcloudappstore.settings.development
	$(manage) importdbtranslations --settings nextcloudappstore.settings.development
