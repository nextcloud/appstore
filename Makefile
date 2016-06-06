# only random once obviously ;)
random=$(shell env LC_CTYPE=C tr -dc "a-zA-Z0-9-_\$\?" < /dev/urandom | head -c 64)
python=venv/bin/python
pip=venv/bin/pip
pycodestyle=venv/bin/pycodestyle
pyresttest=venv/bin/pyresttest
manage=$(python) $(CURDIR)/manage.py

lint:
	$(pycodestyle) $(CURDIR)/nextcloudappstore --exclude=migrations

test: lint
	$(manage) test
	# assume that the testserver is running on port 8001


# Only for local setup, do not use in production
dev-setup:
	pyvenv venv
	@echo "DEBUG = True" > $(CURDIR)/nextcloudappstore/local_settings.py
	@echo "SECRET_KEY = '$(random)'" >> $(CURDIR)/nextcloudappstore/local_settings.py
	$(pip) install -r $(CURDIR)/requirements.txt
	$(pip) install -r $(CURDIR)/dev-requirements.txt
	$(manage) migrate
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.yaml
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell

