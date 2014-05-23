test:
	python manage.py test --settings=talks.settings_test

local:
	python manage.py runserver --settings=talks.local_settings

