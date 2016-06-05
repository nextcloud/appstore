lint:
	pycodestyle nextcloudappstore --exclude=migrations

test: lint
	python3 manage.py test
