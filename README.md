# talks.ox
[![Build Status](https://travis-ci.org/ox-it/talks.ox.svg?branch=master)](https://travis-ci.org/ox-it/talks.ox)
[![Documentation Status](https://readthedocs.org/projects/talksox/badge/?version=latest)](https://readthedocs.org/projects/talksox/?badge=latest)

New version of Oxford Talks

## Developers

System requirements:
 * python 2.7
 * virtualenv (recommended)
 * sqlite (recommended, or alternatively PostgreSQL)
 * phantomjs (mandatory to run functional tests)
 * [Apache Solr](http://lucene.apache.org/solr/) (search server)

Install python dependencies:

    pip install -r requirements.txt
    pip install -r requirements_dev.txt

Create the database:

    python manage.py migrate --settings=talks.settings_dev

Load fixtures (test events):

    python manage.py loaddata talks/events/fixtures/dev_data.yaml --settings=talks.settings_dev

Run development web server:

    make local

Run all tests:

    make test

### Generating the schema for Apache Solr

The file ``schema.xml`` needs to be generated using:

    python manage.py build_solr_schema

### Running Solr

If you have ``Docker`` and ``Fig`` installed, you can start Solr by typing (assuming solr schema):

    fig up solr

The ``solrconfig.xml`` file is available in the ``solr`` directory at the root of the repository.

Both files (``schema.xml`` and ``solrconfig.xml``) need to be put in your core's (default is ``collection1``) ``conf`` directory.
