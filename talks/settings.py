"""
Django settings for talks project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

from __future__ import absolute_import
from .secrets import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

EVENT_DATETIME_FORMAT = "j F Y, G:i"
EVENT_TIME_FORMAT = "H:i"

API_OX_DATES_URL = 'https://api.m.ox.ac.uk/dates/'

DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'

    # Transformed to dd/mm/yyyy for sane people
    '%d/%m/%Y %H:%M:%S',     # '25/10/2006 14:30:59'
    '%d/%m/%Y %H:%M:%S.%f',  # '25/10/2006 14:30:59.000200'
    '%d/%m/%Y %H:%M',        # '25/10/2006 14:30'
    '%d/%m/%Y',              # '25/10/2006'
    '%d/%m/%y %H:%M:%S',     # '25/10/06 14:30:59'
    '%d/%m/%y %H:%M:%S.%f',  # '25/10/06 14:30:59.000200'
    '%d/%m/%y %H:%M',        # '25/10/06 14:30'
    '%d/%m/%y',              # '25/10/06'
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'diq0@tw%t7(vlxo3e65x##2(*29cz22k@_&u9--u69q^g$9j)@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['talks-dev.oucs.ox.ac.uk', 'new.talks.ox.ac.uk', 'talks.ox.ac.uk']

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = '/login'

# Allow cross-origin http GET requests
CORS_ORIGIN_ALLOW_ALL = True

SESSION_COOKIE_AGE = 43200      # 12 hours

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party
    'bootstrapform',
    'haystack',
    'raven.contrib.django.raven_compat',
    'reversion',
    'corsheaders',
    'rest_framework',


    # Oxford Talks
    'talks.users',
    'talks.events',
    'talks.contributors',
    'talks.api_ox',
    'talks.old_talks'
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.PersistentRemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # reversion (audit)
    'reversion.middleware.RevisionMiddleware',

    # Oxford Talks
    'talks.users.middleware.TalksUserMiddleware',

    # CorsHeaders
    'corsheaders.middleware.CorsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'djoxshib.backends.ShibbolethBackend',
    'django.contrib.auth.backends.ModelBackend'
)

ROOT_URLCONF = 'talks.urls'

WSGI_APPLICATION = 'talks.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'talks',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

# NOTE: disabled l10n to get the DATETIME_INPUT_FORMATS working
USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATIC_URL = '/static/'

STATIC_ROOT = '/srv/talks/static/'

TEMPLATES = [
    {
    	'BACKEND': 'django.template.backends.django.DjangoTemplates',
    	'DIRS': [(os.path.join(BASE_DIR, 'talks', 'templates'))],
    	'APP_DIRS': True,
    	'OPTIONS': {
            'context_processors': (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # Added by us
                "django.template.context_processors.request"
            )
        }
    }
]


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_jsonp.renderers.JSONPRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
        'talks.core.renderers.ICalRenderer'
    )
}

# load the collection name from the local file


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/talks',
        'INCLUDE_SPELLING': True,
        'SILENTLY_FAIL': False
    },
}

# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
HAYSTACK_SIGNAL_PROCESSOR = 'talks.events_search.signal_processor.EventUpdateSignalProcessor'

RAVEN_CONFIG = {
    'dsn': 'http://cc958b8c93c340c9a25dd765e1843172:f67c8030f2674d6b9c74718f2abf4c16@sentry.oucs.ox.ac.uk/27',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'oxpoints': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'oxpoints'
    },
    'topics': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'department_descendant': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'department_descendants'
    }
}
