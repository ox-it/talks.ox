from talks.settings import *


INSTALLED_APPS += ('debug_toolbar', 'django_nose')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

RAVEN_CONFIG = {}

LOGIN_URL = '/admin/login'

LOGGING = None
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
