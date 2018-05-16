from .testing import *  # NOQA

DEBUG = True

DATABASES = {
    'default': {
        'NAME': os.path.join(PROJECT_ROOT, 'nhsorganisations.sqlite'),
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
