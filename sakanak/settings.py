"""
إعدادات Django لمشروع سكنك (Sakanak)
مشروع حجز الشقق باللغة العربية مع دعم RTL
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# إعدادات الأمان

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-n4knn*0rg%m^4=j*f8f@n8s0i5a22#%l55o@=n9)4jh@6i3*68')
DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,sakany.pythonanywhere.com').split(',')

# CSRF trusted origins (important on production)
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'https://sakany.pythonanywhere.com'
).split(',')

# Stripe API Keys

# تطبيقات المشروع
INSTALLED_APPS = [
    'jazzmin',  # ثيم لوحة التحكم
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # تطبيقات سكنك
    'accounts',
    'listings', 
    'bookings',
    'payments',
    'pages',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]
# Google OAuth settings
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
LOGIN_REDIRECT_URL = '/'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # دعم اللغات
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.SellerAccessControlMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sakanak.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # مجلد القوالب الرئيسي
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # للصور
            ],
        },
    },
]

WSGI_APPLICATION = 'sakanak.wsgi.application'

# قاعدة البيانات
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# التحقق من كلمات المرور
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

# إعدادات اللغة والوقت (دعم العربية)
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# اللغات المدعومة
LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

# مجلد ملفات الترجمة
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# الملفات الثابتة والوسائط
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# إعدادات الصور والملفات المرفوعة
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# نموذج المستخدم المخصص
AUTH_USER_MODEL = 'accounts.User'

# إعدادات Stripe
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')  # ضع القيمة في ملف .env

# إعدادات تسجيل الدخول
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# إعدادات البريد الإلكتروني
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@sakanak.com')

# إعدادات django-allauth
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PASSWORD_MIN_LENGTH = 8

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Production security (enabled when DEBUG=False)
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Uncomment if you terminate SSL at Django (usually not needed on PythonAnywhere)
    # SECURE_SSL_REDIRECT = True

############################################################
# Jazzmin (Admin) - Force Dark Theme
############################################################
# نجعل لوحة التحكم مظلمة دائمًا باستخدام ثيم Bootswatch "darkly"
JAZZMIN_SETTINGS = {
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    # ثيم افتراضي مظلم
    "theme": "darkly",
    # ثيم الوضع الليلي (نفسه لضمان الغامق دومًا)
    "dark_mode_theme": "darkly",
    # RTL للغة العربية
    "rtl": True,
    # إعدادات شريط التصفح لتلائم الثيم الغامق
    "navbar": "navbar-dark",
    "brand_colour": "navbar-dark",
    # لمسة لون بسيطة
    "accent": "orange",
}

# إعدادات Logging لمتابعة عمليات Stripe
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'stripe_payments.log',
        },
    },
    'loggers': {
        'payments': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

