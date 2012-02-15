from conf.global_settings import *
from bundle_config import config

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": config['postgres']['host'],
        "PORT": int(config['postgres']['port']),
        "USER": config['postgres']['username'],
        "PASSWORD": config['postgres']['password'],
        "NAME": config['postgres']['database'],
    },
}

#EMAIL_HOST = 'office.jaekel-it.de'
#EMAIL_HOST_USER = 'outmail@de.pycon.org'
#EMAIL_HOST_PASSWORD = ''
#EMAIL_PORT = 587


STATIC_ROOT = os.path.join(PROJECT_ROOT, '..', '..', 'data', 'static')
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '..', '..', 'data', 'media')
