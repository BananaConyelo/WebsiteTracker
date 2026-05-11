from .base import *
DEBUG = False
ALLOWED_HOSTS = ['itzzmerov.site']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'e-commerce',
        'USER': 'itzzmerov',
        'PASSWORD': 'password123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}