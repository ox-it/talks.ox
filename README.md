# talks.ox
[![Build Status](https://travis-ci.org/ox-it/talks.ox.svg?branch=master)](https://travis-ci.org/ox-it/talks.ox)
[![Documentation Status](https://readthedocs.org/projects/talksox/badge/?version=latest)](https://readthedocs.org/projects/talksox/?badge=latest)

New version of Oxford Talks

## Start a local instance quickly on OS X

### Initial setup

Assuming that [VirtualBox](https://www.virtualbox.org) and [HomeBrew](http://brew.sh) are installed.

Make sure that you have the latest version of formulas in homebrew:

    brew update

Install docker from the docker website.

### Starting the virtual machine when required

Start the virtual machine:

    eval $(docker-machine env default)
    docker-machine start default

### Starting the project instance when required

This requires the virtual machine to be up (either manually started or when your computer starts).

Type the following command in a terminal:

    docker-machine ip
    
This will give you the IP address of the virtual machine (e.g. `192.168.59.103`), you will need
this information later.

Go at the root of your project directory (probably `talks.ox`):

    docker-compose up
    
After a few seconds (minutes if it is building the instance for the first time), you should be able to visit
in your web browser: `http://<IP ADDRESS>:8000` and visualise Oxford Talks.

If you have a user account (see below), the correct login page is `http://<IP ADDRESS>:8000/admin/login`,
the `Login` link won't work.

Any modification done in the python code/CSS/templates should immediately be visible when you refresh
the page in the web browser.

### Creating the database

Type the following command at the root of your project directory:

    docker-compose run web python manage.py migrate --settings=talks.settings_docker

### Creating a user account

Type the following command at the root of your project directory:

    docker-compose run web python manage.py createsuperuser --username=myusername --email=my@email.com --settings=talks.settings_docker

You will interactively be asked for a password.

## Developers

If you do not want to use the docker setup, make sure that you have the following dependencies available:

 * python 2.7
 * virtualenv (recommended)
 * sqlite (recommended, or alternatively PostgreSQL)
 * phantomjs (mandatory to run functional tests)
 * [Apache Solr](http://lucene.apache.org/solr/) (search server)

Install python dependencies:

    pip install -r requirements.txt
    pip install -r requirements_dev.txt

### Note for Ubunutu-based developers:
If you're installing on an ubuntu linux machine, you may experience errors when pip encounters the psycopg2 and ldap packages.
To prevent this, ensure you install the dev versions of python and libpq.
```
    sudo apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
```

Create the database:

    python manage.py migrate --settings=talks.settings_dev

Load fixtures (test events):

    python manage.py loaddata talks/events/fixtures/dev_data.yaml --settings=talks.settings_dev

Run development web server:

    make local

Run all tests:

    make test

## Using Solr

See `solr/README.md`

## Deployment

SSH key needs to be on the server for the talks user (talks@talks-prod.oucs.ox.ac.uk)

```
fab production deploy:master
```
