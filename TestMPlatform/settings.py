"""
Django settings for TestMPlatform project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import os
import sys
import djcelery

DEBUG = False
# Build paths inside the project like this: os.patMIDDLEWAREh.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(BASE_DIR, 'apps'))
sys.path.insert(1,os.path.join(BASE_DIR, 'extra_apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '47!%*34-uucdx38$2+6xfo-1rgb!5-2b1=8c+tn49*4nf+e+&p'

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['*']

# Application definition
# AUTHENTICATION_BACKENDS = (
#     'users.views.CustomBackend',
# )
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'case.apps.CaseConfig',
    'users.apps.UsersConfig',
    'manager.apps.ManagerConfig',
    'bugs.apps.BugsConfig',
    'requirement.apps.RequirementConfig',
    'xadmin',
    'crispy_forms',
    'reversion',
    'captcha',
    'DjangoUeditor',
    'mptt',
    'djcelery',
]

MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',    # 放页面的时候,应该放在最前面
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',  # 放到最后一个
]


# CACHES = {
#  'default': {
#   'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',  #指定缓存使用的引擎
#   'LOCATION': 'F:\cache_location',        #指定缓存的路径
#   'TIMEOUT': 300,             # 缓存超时时间(默认为300秒,None表示永不过期)
#   'OPTIONS': {
#    'MAX_ENTRIES': 300,           # 最大缓存记录的数量（默认300）
#    'CULL_FREQUENCY': 3,          # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3）
#   }
#  }
# }CACHES = {
#  'default': {
#   'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',  #指定缓存使用的引擎
#   'LOCATION': 'F:\cache_location',        #指定缓存的路径
#   'TIMEOUT': 300,             # 缓存超时时间(默认为300秒,None表示永不过期)
#   'OPTIONS': {
#    'MAX_ENTRIES': 300,           # 最大缓存记录的数量（默认300）
#    'CULL_FREQUENCY': 3,          # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3）
#   }
#  }
# }
# CACHES = {
#     "default":{
#         "BACKEND":"django_redis.cache.RedisCache",
#         "LOCATION":"redis://192.168.102.45:6379/1",
#         "OPTIONS":{
#             "CLIENT_CLASS":"django_redis.client.DefaultClient"
#         }
#     }
# }

ROOT_URLCONF = 'TestMPlatform.urls'
AUTH_USER_MODEL = 'users.UserProfile'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',

            ],

        },
    },
]

WSGI_APPLICATION = 'TestMPlatform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "testmplatfrom",
        'USER': 'root',
        'PASSWORD': "123456",
        'HOST': "127.0.0.1",
        'PORT': '3306',
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",}
        }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT= 'static' #正确
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "/static/"),
)


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_DIRS = (os.path.join(BASE_DIR, 'media'))

EMAIL_HOST = "smtp.163.com"
EMAIL_PORT = 25
EMAIL_HOST_USER = "meibaocai@163.com"
EMAIL_HOST_PASSWORD = "Blue.Mei@"
EMAIL_USE_TLS = False
EMAIL_FROM = "meibaocai@163.com"

# # 异步任务队列Celery在Django中的使用配置
BROKER_URL = 'amqp://yoho:yoho@192.168.102.45:5672/yoho'
RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# djcelery.setup_loader()
# CELERY_ENABLE_UTC = True
# CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_DEFAULT_QUEUE = 'run_api_case'
# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
# CELERY_ACCEPT_CONTENT = ['application/json']
# # CELERY_TASK_SERIALIZER = 'json'
# # CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TASK_RESULT_EXPIRES = 7200  # celery任务执行结果的超时时间，
# CELERYD_CONCURRENCY = 10 if DEBUG else 10 # celery worker的并发数 也是命令行-c指定的数目 根据服务器配置实际更改 一般25即可
# CELERYD_MAX_TASKS_PER_CHILD = 200  # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，比如200
