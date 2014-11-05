from talks.settings import *

DEBUG = True

RAVEN_CONFIG = {}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

AUTHENTICATION_BACKENDS = (
    'talks.users.middleware.TestAuthBackend',
    'django.contrib.auth.backends.ModelBackend'
)

API_OX_URL = '/static/mock/oxpoints.json'
TOPICS_URL = '/static/mock/topics.json?'
