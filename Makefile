lint:
	pycodestyle nextcloudappstore --exclude=migrations

test: lint
	python3 manage.py test

test-setup:
	python3 manage.py migrate
	python3 manage.py loaddata nextcloudappstore/**/fixtures/*.yaml
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell

