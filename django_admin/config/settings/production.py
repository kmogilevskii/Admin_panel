from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'movies',
        'USER': 'django',
        'PASSWORD': '12345',
        'HOST': 'db',
        'PORT': '5432',
    }
}

