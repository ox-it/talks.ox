test: cleantests unittest functest

unittest:
	@python manage.py test --settings=talks.settings_test

functest:
	@PYTHONPATH=tests/ BROWSER=firefox DJANGO_SETTINGS_MODULE=talks.settings_test pybot -e todo tests/

local:
	@python manage.py runserver --settings=talks.local_settings

cleantests:
	@rm -f log.html
	@rm -f output.xml
	@rm -f report.html
	@rm -f selenium-screenshot-*
