"""
Django settings for cmdb project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%bx%y7*ase5$jq7=@8%m+e^r!mn3c)lr9)8@j$c9f_5il^bn3t'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'assets',
    'users',
    'rest_framework',
    'rest_framework.authtoken',
    'myworkflows',
    'it_assets',
    'mysql',
    'ops',
    'channels',
    'mptt',
    'webapi',
    'dashboard',
    'api_wechat',
    'jenkins',
    'txcloud',
    'zabbix',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cmdb.cmdbmiddleware.LocalLoginRequiredMiddleware',
]

ROOT_URLCONF = 'cmdb.urls'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

# STATIC_URL = '/static/'
# STATICFILES_DIRS = (
#     BASE_DIR + STATIC_URL,
# )

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))  # site path

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SITE_ROOT, 'templates')],
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

WSGI_APPLICATION = 'cmdb.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'cmdb_test',
        'USER': 'root',  # Not used with sqlite3.
        'PASSWORD': 'test',  # Not used with sqlite3.
        'HOST': '127.0.0.1',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

'''
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
'''

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    ("js", os.path.join(STATIC_ROOT, "js")),
    ("img", os.path.join(STATIC_ROOT, "img")),
    ("images", os.path.join(STATIC_ROOT, "img")),
    ("css", os.path.join(STATIC_ROOT, "css")),
    ("fonts", os.path.join(STATIC_ROOT, "fonts")),
    ("png", os.path.join(STATIC_ROOT, "png")),
)

AUTHENTICATION_BACKENDS = (
    'users.backends.CustomBackend',
    # 'django_auth_ldap.backend.LDAPBackend',
    # 'django.contrib.auth.backends.ModelBackend',
)

EXCLUDE_URLS = ['/user_login/', '/user_login', '/user_logout/', '/user_logout']

LOGIN_URL = '/user_login/'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework.authentication.TokenAuthentication',

    ),
    "DEFAULT_PERMISSION_CLASSES": (
        'rest_framework.permissions.IsAuthenticated',
        'cmdb.api_permissions.ApiPermission',
    )
}


# redis的配置 celery和django channels 都需要用到redis
# 热更新的过程中也需要用到redis作为更新进度的缓存展示
REDIS_URL = 'redis://:xasgfaswgsdgsagssdfs@localhost:6379/0'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = 'xasgfaswgsdgsagssdfs'
REDIS_BACKEND_URL = 'redis://:xasgfaswgsdgsagssdfs@localhost:6379/1'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_URL)],
        },
        "ROUTING": "cmdb.routing.channel_routing",
    },
}

# SaltStack Master API地址
SALT_MASTER_API = "https://127.0.0.1:6666/"
SALT_MASTER_HOST = "127.0.0.1"
SALT_API_USER = "saltapi"
SLAT_API_PASS = "123123"

# 发送消息渠道 0：所有   1：企业qq   2：企业微信
MSG_CHANNEL = 2

# 维护状态，如果为True,则在通过中间件返回一个维护的页面
# MAINTENANCE = True
MAINTENANCE = False

# 是否是测试环境
# 在正式的生产环境，这个值应该是True!
PRODUCTION_ENV = False

# 是否使用新版本工单流程 1：使用  0：不使用
NEW_WORKFLOW = 1

# 会话超时自动退出
# SESSION_COOKIE_AGE = 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*'
)

JENKINS_40_8_HOST = '192.168.90.37:8081'
JENKINS_40_8_URL = 'http://192.168.90.37:8081'
JENKINS_40_15_HOST = '192.168.90.37:8082'
JENKINS_40_15_URL = 'http://192.168.90.37:8082'
# JENKINS_yuanli_extranal_HOST = '192.168.90.37'
# JENKINS_yuanli_extranal_URL = 'https://192.168.90.37/j3'

ZABBIX_HOST = '192.168.90.37'
ZABBIX_URL = 'http://192.168.90.37:8084'

# 是否使用新版版本更新单流程 True-是 False-否
NEW_VERSION_UPDATE = True