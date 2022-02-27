# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os

env_dist = os.environ
import djcelery
from datetime import timedelta
from kombu import Exchange, Queue, binding

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ############################### 环境参数  #############################
if env_dist.get('SHOPPING_ENV') == "DEV":
    print "------------------------"
    DEBUG = True
    ALLOWED_HOSTS = []
    # 日志
    django_info_log = os.path.join(BASE_DIR, 'log', 'info.log')
    django_error_log = os.path.join(BASE_DIR, 'log', 'error.log')
    # redis
    REDIS_HOST = "animal.xhty.site"
    REDIS_PORT = 6379
    REDIS_DB = 0
    DJANGO_MYSQL_HOST = 'animal.xhty.site'


if env_dist.get('SHOPPING_ENV') == "TEST":
    DEBUG = False
    ALLOWED_HOSTS = ['*']
    # 日志
    django_info_log = '/data/logs/shopping/info.log'
    django_error_log = '/data/logs/shopping/error.log'
    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB = 0
    DJANGO_MYSQL_HOST = '127.0.0.1'
    MYSQL_PWD = 'qv8KnAwraUnla10e'

    # 邀请链接 (我服务器上html文件路径)
    INVITE_LINK = "http://animal.xhty.site/Register"
    # 西西支付回调
    ALIFU_NOTIFY_URL = "http://animal.xhty.site/pay/alfnotify/"
    # vip支付回调
    VIPPAY_NOTIFY = "http://animal.xhty.site/pay/vipnotify/"
    XIXI_LINK = "http://www.bill01.com/Pay_Index.html"
    MYSQL_DB = 'shopping'
    # A8支付回调
    A_EIGHT_ASYNC = "http://animal.xhty.site/pay/a_eightnotify/"
    A_EIGHT_SYNC = "http://xxxx"
    A_EIGHT_LINK = "http://api.77feipay.com/api/v1/pay/order"

    # #################################### 七牛 ###################################
    QINIU_ACCESS_KEY = 'h8BESeO6mxQNX-DjMS2YdCBXhwY_c2faJcpq572H'
    QINIU_SECRET_KEY = 'dPorICJ8l_oGsRcnFSF0lGuCgmYXJ8qWGRZuRjy3'
    QINIU_BUCKET_NAME = 'shopping-test'
    QINIU_SECURE_URL = False  # 使用http
    # QINIU_BUCKET_DOMAIN = 'pgstw1k4p.bkt.clouddn.com'
    # IMAGE_PATH = 'http://' + QINIU_BUCKET_DOMAIN + 'image'
    # 图片域名
    STATIC_DOMAIN = "http://img-shopping-test.xhty.site/"

    # admin静态文件url的路径
    STATIC_URL = '/static/'

    # collectstatic 收集admin页面所用
    STATIC_ROOT = '/data/static/'


if env_dist.get('SHOPPING_ENV') == "PRO":
    DEBUG = False
    ALLOWED_HOSTS = ['*']
    # 日志
    django_info_log = '/data/logs/shopping/info.log'
    django_error_log = '/data/logs/shopping/error.log'
    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB = 0
    DJANGO_MYSQL_HOST = '127.0.0.1'
    MYSQL_PWD = 'qv8KnAwraUnla10e'

    # 邀请链接 (我服务器上html文件路径)
    INVITE_LINK = "https://shalilai.cn/Register"
    # 西西支付回调
    ALIFU_NOTIFY_URL = "https://shalilai.cn/pay/alfnotify/"
    ALIFU_CALLBACK_URL = "https://xxxx"
    # vip支付回调
    VIPPAY_NOTIFY = "https://shalilai.cn/pay/vipnotify/"
    XIXI_LINK = "http://www.bill01.com/Pay_Index.html"
    MYSQL_DB = 'shopping'
    # A8支付回调
    A_EIGHT_ASYNC = "https://shalilai.cn/pay/a_eightnotify/"
    A_EIGHT_SYNC = "https://xxxx"
    A_EIGHT_LINK = "http://api.77feipay.com/api/v1/pay/order"

    # #################################### 七牛 ###################################
    QINIU_ACCESS_KEY = 'h8BESeO6mxQNX-DjMS2YdCBXhwY_c2faJcpq572H'
    QINIU_SECRET_KEY = 'dPorICJ8l_oGsRcnFSF0lGuCgmYXJ8qWGRZuRjy3'
    QINIU_BUCKET_NAME = 'shopping'
    QINIU_SECURE_URL = False  # 使用http
    # QINIU_BUCKET_DOMAIN = 'pgstw1k4p.bkt.clouddn.com'
    # IMAGE_PATH = 'http://' + QINIU_BUCKET_DOMAIN + 'image'
    # 图片域名
    STATIC_DOMAIN = "http://r7ygktdfd.hb-bkt.clouddn.com/"

    # admin静态文件url的路径
    STATIC_URL = '/static/djadmin-page/'

    # collectstatic 收集admin页面所用
    STATIC_ROOT = '/data/www/django/static/djadmin-page/'

djcelery.setup_loader()

BROKER_URL = 'redis://' + REDIS_HOST + ':6379/1'
# 无密码 redis://localhost:6379/0 密码 redis://xxxx@localhost:6379/0


# 配置时区
CELERY_TIMEZONE = 'Asia/Shanghai'
# 这是使用了django-celery默认的数据库调度模型,任务执行周期都被存在你指定的orm数据库中
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
# 定义一个夺宝项目的交换机
st_exchange = Exchange('snatchtreasure', type='direct')
statistics_exchange = Exchange('statistics', type='direct')
user_exchange = Exchange('user', type='direct')
pay_exchange = Exchange('pay', type='direct')
activity_exchange = Exchange('activity', type='direct')

# 创建队列
CELERY_QUEUES = (
    # 发送验证码
    Queue(name='sms', exchange=user_exchange, routing_key="sms"),
    # 增加机器人余额
    Queue(name='increment_robot_balance', exchange=user_exchange,
          routing_key="increment_robot_balance"),
    # 注册赠送
    Queue(name='signup_present', exchange=user_exchange,
          routing_key="signup_present"),

    # 分配夺宝号
    Queue(name='allocation_token', exchange=st_exchange,
          routing_key='allocation_token'),
    # 缓存荣誉榜
    # Queue(name='cache_honor_list', exchange=st_exchange,
    #       routing_key='cache_honor_list'),

    # 活动
    Queue(name='activity', exchange=activity_exchange, routing_key='presents'),

    # 发送充值通知短信
    Queue(name='pay', exchange=pay_exchange, routing_key="pay_success"),

    # 玩家数据
    Queue(name='statistics_player_everyday_data', exchange=statistics_exchange,
          routing_key="statistics_player_everyday_data"),
    Queue(name='statistics_player_data', exchange=statistics_exchange,
          routing_key="statistics_player_data"),
    Queue(name='statistics_month_player_data', exchange=statistics_exchange,
          routing_key="statistics_month_player_data"),

    # 回收商数据
    Queue(name='statistics_rb_everyday_data', exchange=statistics_exchange,
          routing_key="statistics_rb_everyday_data"),
    Queue(name='calcul_business_today_data', exchange=statistics_exchange,
          routing_key="calcul_business_today_data"),

    # 平台数据
    Queue(name='statistics_platform_data', exchange=statistics_exchange,
          routing_key="statistics_platform_data"),
    Queue(name='improve_yesterday_platform_data', exchange=statistics_exchange,
          routing_key="improve_yesterday_platform_data")
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cj7zhmilyc)lw6#j!$ps^zlhk_0m)oa2njl+-!^2pwt6*h1#db'

# SECURITY WARNING: don't run with debug turned on in production!


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'djcelery',
    'activitys',
    'financial',
    'inventory',
    'resources',
    'rest',
    'shopping_settings',
    'shopping_user',
    'statistics',
    'snatch_treasure',
    'recycle_businessman',
    'pay'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware'
]

# ##################################### 跨域  ##################################
# 使用django rest framework 需要配置CSRF_COOKIE_NAME, CSRF_HEADER_NAME
# 配置SessionAuthentication来鉴权
CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "CSRF_COOKIE"

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*'
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
    'Cookie',
    'Accept',
    'Token'
)

ROOT_URLCONF = 'shopping.urls'

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

WSGI_APPLICATION = 'shopping.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MYSQL_DB,
        'USER': 'root',
        'PASSWORD': MYSQL_PWD,
        'HOST': DJANGO_MYSQL_HOST,
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'  # 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# USE_TZ = True

AUTH_USER_MODEL = 'shopping_user.UserProfileBasic'

# STATICFILES_DIRS = (
#     # 指出要引用的资源所在目录名字.(这个就是实际目录名,和引用指针名无关)
#     os.path.join(BASE_DIR, 'static'),
# )
# ######################### rest framework ###################################
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',)
}


# ############################ 其他 ##########################################
# 聚合数据,查询IP归属地
JUHE_DATA_KEY = "354738ca12d20c302093cd5f732e5a79"

# 极光短信
JSMS_URL = "https://api.sms.jpush.cn/v1/messages"
J_APPKEY = "58af5b3e94e5207901182af8"
J_APPSECRET = "c6325c4516cd82f6f7bc60b0"

# 极光推送
NOTIFY_APP_KEY = '58af5b3e94e5207901182af8'
NOTIFY_SCRECT_KEY = 'c6325c4516cd82f6f7bc60b0'

# 临时文件路径
TMP_PATH = '/data/tmp'

# 西西支付key
ALIFU_KEY = "m8swl81p4tfcxxa6ydxpbmltexia9rdt"

# VIP支付
DESKEY = 'RiUUAVdP'
MD5KEY = "cp2SJmsZ"
SYSPWD = "158940"
MERCHANT_NO = "S20190327131318"

# A8支付
A_EIGHT = 'http://api.77feipay.com/api/v1/pay/order'
A_EIGHT_KEY = '53E48FDC8D3B4AA79B8EBB7258D44635'

# 喵嘀短信
MD_ACCOUNT_SID = '5c549a31d5ce95f4de323cfecb24b82a'
MD_ACCT_KEY = '758e7be09fcb2dc9dfdc88cfdb3b3507'

# ############################ 日志 ##########################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-8s %(message)s'
        },
        'detail': {
            'format': '%(asctime)s %(levelname)-8s %(pathname)s[line:%(lineno)d] %(message)s'
        },
    },
    # 所有包的error info
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': django_info_log,
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 100,
            'formatter': 'detail',
        },
        'error': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': django_error_log,
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 100,
            'formatter': 'detail',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'info'],
            'level': 'INFO',
            'propagate': True,
        },
        'statistics': {
            'handlers': ['console', 'error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'pay': {
            'handlers': ['console', 'error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'shopping_user': {
            'handlers': ['console', 'error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'snatch_treasure': {
            'handlers': ['console', 'error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'utils': {
            'handlers': ['console', 'error'],
            'level': 'ERROR',  # 这个包里面低于这个level的logger信息就不会记录
            'propagate': True,
        },
        'shopping_settings': {
            'handlers': ['console', 'error'],
            'level': 'ERROR',
            'propagate': True,
        },

    },
}

DEFAULT_HEAD_IMG = "headimg/default1.jpg"
