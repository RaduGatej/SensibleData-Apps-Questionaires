# Django settings for questionnaires project.

import os
import LOCAL_SETTINGS

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Piotr Sapiezynski', 'pisa@dtu.dk'),
)


BASE_DIR = LOCAL_SETTINGS.BASE_DIR
ROOT_DIR = LOCAL_SETTINGS.ROOT_DIR
ROOT_URL = LOCAL_SETTINGS.ROOT_URL
SURVEY_DIR = LOCAL_SETTINGS.SURVEY_DIR
SURVEY_FILE = LOCAL_SETTINGS.SURVEY_FILE
OUR_QUESTIONS = LOCAL_SETTINGS.OUR_QUESTIONS
DATABASES = LOCAL_SETTINGS.DATABASES
DO_AUTH = LOCAL_SETTINGS.DO_AUTH

MANAGERS = ADMINS

LOGIN_URL = ROOT_URL+'openid/login/'
LOGIN_REDIRECT_URL = ROOT_URL
OPENID_SSO_SERVER_URL = LOCAL_SETTINGS.OPENID_SSO_SERVER_URL
OPENID_USE_EMAIL_FOR_USERNAME = False
AUTHENTICATION_BACKENDS = (
            'django_openid_auth.auth.OpenIDBackend',
            'django.contrib.auth.backends.ModelBackend',
        )

def failure_handler_function(request, message, status=None, template_name=None, exception=None):
	from django.shortcuts import redirect
	from django.http import HttpResponse
	registration = request.REQUEST.get('registration', False)
	if registration: return redirect('login')
	return redirect('openid_failed')

OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = False
OPENID_RENDER_FAILURE = failure_handler_function

APPEND_SLASH = True

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [".sensible.dtu.dk"]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Copenhagen'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ROOT_DIR+'static_root'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = ROOT_URL+'static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	ROOT_DIR+'static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.static',
	'django.contrib.auth.context_processors.auth',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = LOCAL_SETTINGS.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'questionnaires.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'questionnaires.wsgi.application'

TEMPLATE_DIRS = (
    ROOT_DIR+'templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_openid_auth',
    'render',
    'backend',
    'utils',
    'bootstrap_toolkit',
    'south',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

import hashlib
SESSION_COOKIE_NAME = str(hashlib.sha1(SECRET_KEY).hexdigest())
