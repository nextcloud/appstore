poetry=poetry
poetry_run=$(poetry) run
python=$(poetry_run) python
pyresttest=$(poetry_run) pyresttest
coverage=$(poetry_run) coverage
manage-script=$(CURDIR)/manage.py
manage=$(poetry_run) $(manage-script)
db=sqlite
npm=npm
prod_version=27.0.0

.PHONY: test
test:
	$(npm) test
	$(coverage) run --source=nextcloudappstore $(manage-script) test --settings nextcloudappstore.settings.development -v 2
	$(coverage) report --fail-under 90

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
	rm -f db.sqlite3
	$(npm) install
	$(npm) run build
	$(poetry) install
	cp $(CURDIR)/scripts/development/settings/base.py $(CURDIR)/nextcloudappstore/settings/development.py
	cat $(CURDIR)/scripts/development/settings/$(db).py >> $(CURDIR)/nextcloudappstore/settings/development.py
	$(MAKE) initdb
	$(MAKE) l10n


.PHONY: initdb
initdb:
	$(manage) migrate --settings nextcloudappstore.settings.development
	$(manage) loaddata $(CURDIR)/nextcloudappstore/core/fixtures/*.json --settings nextcloudappstore.settings.development
	$(manage) createsuperuser --username admin --email admin@admin.com --noinput --settings nextcloudappstore.settings.development
	$(manage) verifyemail --username admin --email admin@admin.com --settings nextcloudappstore.settings.development
	$(manage) setdefaultadminpassword --settings nextcloudappstore.settings.development

.PHONY: docs
docs:
	$(MAKE) -C $(CURDIR)/docs/ clean html

.PHONY: update-dev-deps
update-dev-deps:
	$(poetry) upgrade
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

.PHONY: test-data
test-data: test-user
	PYTHONPATH="${PYTHONPATH}:$(CURDIR)/scripts/" $(python) -m development.testdata

.PHONY: prod-data
prod-data:
	PYTHONPATH="${PYTHONPATH}:$(CURDIR)/scripts/" $(python) -m development.proddata $(prod_version)

.PHONY: l10n
l10n:
	$(manage) compilemessages --settings nextcloudappstore.settings.development
	$(manage) importdbtranslations --settings nextcloudappstore.settings.development

.PHONY: coverage
coverage:
	$(coverage) xml

.PHONY: test-user
test-user:
	$(manage) createtestuser --username user1 --password user1 --email user1@user.com --settings nextcloudappstore.settings.development
	$(manage) createtestuser --username user2 --password user2 --email user2@user.com --settings nextcloudappstore.settings.development
	$(manage) createtestuser --username user3 --password user3 --email user3@user.com --settings nextcloudappstore.settings.development
