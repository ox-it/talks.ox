talks.ox
========
[![Build Status](https://travis-ci.org/ox-it/talks.ox.svg?branch=master)](https://travis-ci.org/ox-it/talks.ox)
[![Documentation Status](https://readthedocs.org/projects/talksox/badge/?version=latest)](https://readthedocs.org/projects/talksox/?badge=latest)

New version of Oxford Talks

Requirements
------------

See requirements.txt

Currently using Django 1.7 beta 4


Use of Apache Solr
------------------

Apache Solr is used to provide the search functionnalities of the website.

You can download it from the [main website](http://lucene.apache.org/solr/).

The ``schema.xml`` needs to be generated using:
  
    python manage.py build_solr_schema

The ``solrconfig.xml`` file is available in the ``solr`` directory at the root of the repository.

Both files (``schema.xml`` and ``solrconfig.xml``) need to be put in your core's (default is ``collection1``) ``conf`` directory.

Developers
----------

* Requirements: python 2.7, virtualenv, sqlite
* Install dependencies: ``pip install -r requirements.txt`` && ``pip install -r requirements_dev.txt``
* Create the database: ``python manage.py migrate --settings=talks.settings_dev``
* Load fixtures (test events): ``./manage.py loaddata talks/events/fixtures/dev_data.yaml --settings=talks.settings_dev``
* Run web server: ``./manage.py runserver --settings=talks.settings_dev``
