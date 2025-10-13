# config/settings.py
import os
from pathlib import Path
from decouple import config, Csv

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Segurança / Debug ---
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Domínios permitidos
ALLOWED_HOSTS = ['picsart.com.br', 'www.picsart.com.br', '168.231.92.3', 'srv1043318.hstgr.cloud']

# Confiar no host/protocolo repassado pelo Nginx (proxy)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF confia em seus domínios HTTPS
CSRF_TRUSTED_ORIGINS = ['https://picsart.com.br', 'https://www.picsart.com.br']

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Banco de Dados (PostgreSQL via .env) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# --- Senhas ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n / tz ---
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --- App sob /blockline (subcaminho) ---
FORCE_SCRIPT_NAME = os.getenv('SCRIPT_NAME', '/blockline')

# --- Arquivos estáticos e mídia sob /blockline ---
STATIC_URL = f"{FORCE_SCRIPT_NAME}/static/"
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL  = f"{FORCE_SCRIPT_NAME}/media/"
MEDIA_ROOT  = BASE_DIR / 'media'

# --- Auth (URLs sob /blockline) --
LOGIN_URL = f"{FORCE_SCRIPT_NAME}/accounts/login/"
LOGIN_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"
LOGOUT_REDIRECT_URL = f"{FORCE_SCRIPT_NAME}/"

# --- Primary key padrão ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Cookies seguros quando atrás de HTTPS ---
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

