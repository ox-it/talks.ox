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

### Using Solr

See `solr/README.md`
