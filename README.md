talks.ox
========
[![Build Status](https://travis-ci.org/ox-it/talks.ox.svg?branch=master)](https://travis-ci.org/ox-it/talks.ox)

New version of Oxford Talks

Requirements
------------

See requirements.txt

Currently using Django 1.7 beta 4


Developers
----------

* Requirements: python 2.7, virtualenv, sqlite
* Install dependencies: ``pip install -r requirements.txt`` && ``pip install -r requirements_dev.txt``
* Create the database: ``python manage.py migrate --settings=talks.settings_dev``
* Load fixtures (test events): ``./manage.py loaddata talks/events/fixtures/dev_data.yaml --settings=talks.settings_dev``
* Run web server: ``./manage.py runserver --settings=talks.settings_dev``
