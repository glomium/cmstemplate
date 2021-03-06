"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

from importlib import import_module

import os
import re


gettext = lambda s: s  # NOQA
BASE_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
PROJECT_NAME = os.environ.get('PROJECT_NAME', os.path.basename(BASE_DIR))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

SITE_ID = 1
ALLOWED_HOSTS = '*'
INTERNAL_IPS = ('127.0.0.1', '37.120.177.229')

DEBUG = False  # default debug setting

# Application definition

INSTALLED_APPS = [
    # custom (swapped)
    'useraccounts',

    # django modules
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',

    # 3rd party
    'rest_framework',
    'cms',
    'menus',
    'treebeard',
    'sekizai',
    'djangocms_history',

    # own
    'filemanager',
]

AUTH_USER_MODEL = "useraccounts.User"
AUTHENTICATION_BACKENDS = ['useraccounts.backends.AuthBackend']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.middleware.PrivacyMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
]

ROOT_URLCONF = 'app.urls'

ADMINS = (
    ('Sebastian Braun', 'sebastian@elmnt.de'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            # Display fancy error pages, when DEBUG is on
            'debug': True,
            'context_processors': [
                # adds 'user' and 'perms' to request
                'django.contrib.auth.context_processors.auth',
                # if debug is true, sql_queries is added to the request
                'django.template.context_processors.debug',
                # add LANGUAGES and LANGUAGE_CODE to request
                'django.template.context_processors.i18n',
                # add MEDIA_URL to request
                'django.template.context_processors.media',
                # add STATIC_URL to request
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                # adds the request object to the request
                'django.template.context_processors.request',
                # adds messages to the request
                'django.contrib.messages.context_processors.messages',

                # adds the DoNotTrack as variable to the context
                'app.context_processors.dnt',

                'cms.context_processors.cms_settings',
                'sekizai.context_processors.sekizai',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

# CMS =========================================================================

CMS_TEMPLATES = [
    ("template_clean.html", gettext("Clean Template")),
]
CMS_PERMISSION = True
CMS_TOOLBAR_ANONYMOUS_ON = False

LANGUAGES = [
    ('de', "Deutsch"),
]


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

LANGUAGE_CODE = 'de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

FILEMANAGER_SENDTYPE = "xaccel"

FILEMANAGER_STORAGE_ROOT = os.path.join(BASE_DIR, "storage")
FILEMANAGER_STORAGE_URL = "/storage/"

FILEMANAGER_CACHE_ROOT = os.path.join(BASE_DIR, "cached")
FILEMANAGER_CACHE_URL = "/cached/"


# LOGGING =========================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'formatter': 'verbose',
        },
        'systemd': {
            'class': 'systemd.journal.JournaldLogHandler',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['systemd'],
        'level': 'DEBUG',
    },
    'loggers': {
        # Log messages related to the handling of requests.
        # 5XX responses are raised as ERROR messages;
        # 4XX responses are raised as WARNING messages.
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # # same as django.request, but only for runserver
        # 'django.server': {
        #     'handlers': ['console'],
        #     'propagate': True,
        # },
        # log sql performance
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': True,
        },
    }
}


# FILER =======================================================================

FILER_STORAGES = {
    'public': {
        'main': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': MEDIA_ROOT,
                'base_url': MEDIA_URL,
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': 'filer',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PublicFileSystemStorage',
            'OPTIONS': {
                'location': MEDIA_ROOT,
                'base_url': MEDIA_URL,
            },
            'THUMBNAIL_OPTIONS': {
                'base_dir': 'thumbnails',
            },
        },
    },
}

TEXT_SAVE_IMAGE_FUNCTION = 'cmsplugin_filer_image.integrations.ckeditor.create_image_plugin'

THUMBNAIL_PROCESSORS = (

    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    # 'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
    'easy_thumbnails.processors.background',
)


THUMBNAIL_QUALITY = 85

# CMS TEMPLATE ====================================================================

CMSTEMPLATE_SITEMAPS = {
    'cmspages': 'cms.sitemaps.CMSSitemap',
}


# LOCAL SETTINGS ==================================================================

try:
    from .local_settings import *  # NOQA
except ImportError:
    SECRET_KEY = 'just-a-dummy-key-overwrite-it-in:local_settings.py'

    # Database
    # https://docs.djangoproject.com/en/dev/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '%s/database.sqlite' % BASE_DIR,
        }
    }

    DEBUG = True

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }


# SESSION =====================================================================

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
if 'MEMCACHED_PORT_11211_TCP_ADDR' in os.environ:  # pragma: no cover
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
           'KEY_PREFIX': PROJECT_NAME,
           'LOCATION': '%s:%s' % (
                os.environ.get('MEMCACHED_PORT_11211_TCP_ADDR'),
                os.environ.get('MEMCACHED_PORT_11211_TCP_PORT', 11211),
           ),
        },
    }


if DEBUG:
    try:
        import_module("debug_toolbar")
        DEBUG_TOOLBAR = True
    except ImportError:
        DEBUG_TOOLBAR = False
else:
    DEBUG_TOOLBAR = False

custom = import_module(".settings_custom", __package__)

if hasattr(custom, 'INSTALLED_APPS'):
    INSTALLED_APPS += custom.INSTALLED_APPS

if hasattr(custom, 'CMSTEMPLATE_SITEMAPS'):
    CMSTEMPLATE_SITEMAPS.update(custom.CMSTEMPLATE_SITEMAPS)

for i in dir(custom):
    if i in ['INSTALLED_APPS', 'CMSTEMPLATE_SITEMAPS']:
        continue

    if not re.match(r'^[A-Z][A-Z0-9_]*[A-Z0-9]$', i):
        continue

    globals()[i] = getattr(custom, i)


# DYNAMIC SETTINGS ============================================================

if "cmsplugin_markdown" in INSTALLED_APPS:
    CMS_TEMPLATES += [
        ("cmsplugin_markdown/base.html", gettext("Documentation")),
    ]

if "cmsplugin_material" in INSTALLED_APPS:
    CMS_TEMPLATES = [
        ("cmsplugin_material/base.html", gettext("Material Design")),
    ] + CMS_TEMPLATES

if "MANAGERS" not in globals():
    MANAGERS = ADMINS

if DEBUG:
    LOGGING['root']['handlers'] += ['console']

if DEBUG_TOOLBAR:
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    DEBUG_TOOLBAR_CONFIG = {
        'JQUERY_URL': None,
    }
else:
    MIDDLEWARE = [
        'cms.middleware.utils.ApphookReloadMiddleware',
    ] + MIDDLEWARE
