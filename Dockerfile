FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD requirements_dev.txt /code/
RUN apt-get update && apt-get install -y git python-dev python-ldap libldap2-dev libsasl2-dev
RUN pip install -r requirements.txt
RUN pip install -r requirements_dev.txt
ADD . /code/

