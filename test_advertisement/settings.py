"""
Django settings for test_advertisement project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_u7^@s^a0*#fqjbcne7h*m*fgyek24^%6lh%1t7evb$a&8&b=3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'texts',
    'moderation',
    'storages',
    'audio_advertising'

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'test_advertisement.urls'

WSGI_APPLICATION = 'test_advertisement.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

LOGIN_URL = '/admin/login/'

MODERATORS_GROUP = "Moderator"
ADVERTISER_GROUP = "Advertiser"

FIXTURE_DIRS = {os.path.join(BASE_DIR, '/moderation/fixtures')}

TEMPLATE_DIRS = {
    os.path.join(BASE_DIR, 'test_advertisement/templates'), }

# Settings for Django-storages
from boto.s3.connection import NoHostProvided

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = '8XK4DJR_KVR7UT6TYWGV'
AWS_SECRET_ACCESS_KEY = 'KzUOLwf-L3YcExTGA4w0FIQXcSaSoQ4zSjGNQA=='
AWS_STORAGE_BUCKET_NAME = 'audioadvertising'
AWS_AUTO_CREATE_BUCKET = True
AWS_S3_HOST = NoHostProvided
AWS_S3_USE_SSL = False
AWS_S3_SECURE_URLS = False
AWS_DEFAULT_ACL = 'public-read-write'
AWS_S3_PROXY_HOST = '127.0.0.1'
AWS_S3_PROXY_PORT = 8080
AWS_S3_CUSTOM_DOMAIN = '%s:%s/%s' % (AWS_S3_PROXY_HOST, AWS_S3_PROXY_PORT, AWS_STORAGE_BUCKET_NAME)
