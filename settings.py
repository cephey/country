import os
import forum.celery  # noqa
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gmwhl5s&^ea7jqy5!00l1hnw$t7%5d@6x!u*%k$9v((&stu%m@'

DEBUG = True
if 'PROD' in os.environ:
    DEBUG = False

INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS = ['95.85.18.34', '188.120.255.63', 'localhost']
if 'PROD' in os.environ:
    ALLOWED_HOSTS.append('forum-msk.org')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'apps.articles',
    'apps.authors',
    'apps.bloggers',
    'apps.forum',
    'apps.pages',
    'apps.polls',
    'apps.tags',
    'apps.users',
    'apps.utils',
    'apps.votes',
    'apps.pda',

    'captcha',
    'ckeditor',
    'cacheback',
    'capture_tag',

    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.utils.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if 'PROD' not in os.environ:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware'
    ] + MIDDLEWARE

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.utils.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'country',
        'USER': 'ptitsyn',
        'PASSWORD': '6HXDc78o'
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
]

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/storage/'

AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

LOGGING_PATH = os.path.join(BASE_DIR, '../django_error.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGGING_PATH,
        },
        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# REDIS
if 'PROD' in os.environ:
    REDIS_DB = 0
elif 'L' in os.environ:  # test
    REDIS_DB = 4
else:
    REDIS_DB = 3
REDIS_LOCATION = 'redis://127.0.0.1:6379/{}'.format(REDIS_DB)

DJANGO_CACHE_VERSION = 2
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'VERSION': DJANGO_CACHE_VERSION,
    }
}

# CELERY
BROKER_URL = REDIS_LOCATION
if 'PROD' not in os.environ:
    CELERY_ALWAYS_EAGER = True

CELERYBEAT_SCHEDULE = {
    'download_latest_entries': {
        'task': 'download_latest_entries',
        'schedule': crontab(minute=11)
    },
    'download_latest_partners_videos': {
        'task': 'download_latest_partners_videos',
        'schedule': crontab(minute=41)
    }
}


if 'L' in os.environ:  # test
    CAPTCHA_TEST_MODE = True

# MIGRATE_FILE_ENCODING = 'koi8-r'
MIGRATE_FILE_ENCODING = 'utf-8'
