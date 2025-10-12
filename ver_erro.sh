#!/bin/bash
# Script para diagnosticar erro do dashboard

echo "=========================================="
echo "  DIAGNÓSTICO DE ERRO - DASHBOARD"
echo "=========================================="
echo ""

echo "1️⃣ Verificando versão do código..."
git log --oneline -1
echo ""

echo "2️⃣ Verificando quantidade de empresas no banco..."
python manage.py shell -c "from core.models import Empresa; print(f'Total de empresas: {Empresa.objects.count()}')" 2>&1
echo ""

echo "3️⃣ Verificando se usuário está autenticado..."
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Total de usuários: {User.objects.count()}')" 2>&1
echo ""

echo "4️⃣ Últimos erros do Gunicorn (últimas 50 linhas com ERROR)..."
sudo journalctl -u gunicorn | grep -i "ERROR" | tail -50
echo ""

echo "5️⃣ Erro específico do dashboard (últimas 30 linhas de contexto)..."
sudo journalctl -u gunicorn | grep -A 30 "Erro no dashboard" | tail -50
echo ""

echo "6️⃣ Status dos serviços..."
echo "--- Gunicorn ---"
sudo systemctl status gunicorn --no-pager | head -10
echo ""
echo "--- Nginx ---"
sudo systemctl status nginx --no-pager | head -10
echo ""

echo "=========================================="
echo "  FIM DO DIAGNÓSTICO"
echo "=========================================="
echo ""
echo "💡 DICA: Copie toda a saída deste script e me envie!"
