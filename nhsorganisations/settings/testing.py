from .base import *  # NOQA

DEBUG = False
SITE_ID = 1

DATABASES = {
    'default': {
        'NAME': os.path.join(PROJECT_ROOT, 'tests', 'nhsorganisations-testing.sqlite'),
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS += (
    'nhsorganisations.tests',
)

ROOT_URLCONF = 'nhsorganisations.tests.urls'
