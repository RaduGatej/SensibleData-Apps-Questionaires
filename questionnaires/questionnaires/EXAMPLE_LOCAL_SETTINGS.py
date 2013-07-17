import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = '/home/user/questionnaires/'
ROOT_URL = '/apps/questionnaire/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ROOT_DIR+'SECURE_data.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

#import uuid, hashlib
#str(hashlib.sha256(str(uuid.uuid4())).hexdigest())
SECRET_KEY = '1234'

OPENID_SSO_SERVER_URL = 'http://example.com/'
