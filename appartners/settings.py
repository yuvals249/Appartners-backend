"""
Django settings for appartners project.

Generated by 'django-admin startproject' using Django 1.10.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from datetime import timedelta
import json
import tempfile

import environ
import firebase_admin
from firebase_admin import credentials

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
if os.path.exists(os.path.join(BASE_DIR, '.env')):
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

FIREBASE_CONFIG = json.loads(env('FIREBASE_CONFIG'))

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [

    # Channels for WebSockets
    'channels',
    'daphne',


    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'django_extensions',

    # apps
    'users',
    'apartments',
    'chat',

    'rest_framework',
    'cloudinary',
    'cloudinary_storage',
    'rest_framework.authtoken',

    # Chat visualization at the backend
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'appartners.http_jwt_middleware.JWTAuthMiddleware',  # JWT authentication middleware
    'appartners.middleware.RequestResponseLoggingMiddleware',
    'appartners.middleware.UserPresenceMiddleware',

    # Chat visualization at the backend
    'corsheaders.middleware.CorsMiddleware',
]

# # Chat visualization at the backend
# CORS_ALLOW_ALL_ORIGINS = True  # Only for development!

# Chat visualization at the backend
if not DEBUG:
    CORS_ALLOW_ALL_ORIGINS = False  # Only for development!


ROOT_URLCONF = 'appartners.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'appartners.wsgi.application'
ASGI_APPLICATION = 'appartners.asgi.application'

# Channel layers for WebSockets

# Use REDIS_URL env var in production; fallback to in-memory channel layer locally
redis_url = env('REDIS_URL', default=None)

if redis_url:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [redis_url],
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='MY_DB'),  # Database name
        'USER': env('DB_USER', default='MY_USER'),  # Database user
        'PASSWORD': env('DB_PASSWORD', default='MY_PASSWORD'),  # Database password
        'HOST': env('DB_HOST', default='localhost'),  # Database host, default to localhost
        'PORT': env('DB_PORT', default='5432'),  # Database port, default to 5432
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Cloudinary configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'appartners': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apartments': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'chat': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'chat.authentication.JWTAuthentication',
    ],
}

# Custom authentication backends
AUTHENTICATION_BACKENDS = [
    'users.auth.CaseInsensitiveEmailBackend',  # Our custom email auth backend
    'django.contrib.auth.backends.ModelBackend',  # Default backend
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@appartners.com')

# FIREBASE_CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'firebase_config.json')


# cred = credentials.Certificate(FIREBASE_CONFIG)
# initialize_app(cred)

# Initialize Firebase securely from FIREBASE_CONFIG (JSON string)
if not firebase_admin._apps:  # Check if Firebase is not already initialized
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
        json.dump(FIREBASE_CONFIG, temp_file)
        temp_file_path = temp_file.name

    cred = credentials.Certificate(temp_file_path)
    firebase_admin.initialize_app(cred)

    # Clean up the temp file after use (optional but recommended)
    os.unlink(temp_file_path)
