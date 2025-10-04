@echo off
echo ========================================
echo   TESTE LOCAL - Historico de Estoque
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Criando banco de dados de desenvolvimento...
.\venv\Scripts\python.exe manage.py migrate --settings=config.settings_dev

echo.
echo [2/4] Coletando arquivos estaticos...
.\venv\Scripts\python.exe manage.py collectstatic --noinput --settings=config.settings_dev

echo.
echo [3/4] Verificando se precisa criar superuser...
echo Para criar superuser, execute: .\venv\Scripts\python.exe manage.py createsuperuser --settings=config.settings_dev

echo.
echo [4/4] Iniciando servidor de desenvolvimento...
echo Acesse: http://localhost:8000
echo.
.\venv\Scripts\python.exe manage.py runserver --settings=config.settings_dev

pause
