from talks.settings import *


INSTALLED_APPS += ('debug_toolbar',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

RAVEN_CONFIG = None

LOGGING = None
