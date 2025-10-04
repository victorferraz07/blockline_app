# Configurações de DESENVOLVIMENTO
# NÃO USAR EM PRODUÇÃO!

from .settings import *

# Sobrescrever configurações para desenvolvimento
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Banco de dados SQLite local (para não afetar produção)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_dev.sqlite3',
    }
}

# Desabilitar segurança HTTPS em dev
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
