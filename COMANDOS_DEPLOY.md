# 🚀 Comandos para Deploy - PWA Fase 2

## ⚠️ IMPORTANTE: Execute estes comandos em ordem!

---

## 1️⃣ Ativar Ambiente Virtual

### Windows (PowerShell/CMD)
```bash
cd c:\Users\Rafael\django_user\blockline_app
venv\Scripts\activate
```

### Linux/Mac
```bash
cd /caminho/do/projeto
source venv/bin/activate
```

Você verá `(venv)` no início da linha de comando.

---

## 2️⃣ Coletar Arquivos Estáticos

```bash
cd blockline_app
python manage.py collectstatic --noinput
```

**O que isso faz:**
- Copia todos os arquivos de `core/static/` para a pasta `static/`
- Inclui os 3 novos scripts PWA:
  - `pwa-notifications.js`
  - `pwa-camera-scanner.js`
  - `pwa-geolocation.js`

**Resultado esperado:**
```
120 static files copied to 'c:\Users\Rafael\django_user\blockline_app\blockline_app\static'.
```

---

## 3️⃣ (Opcional) Aplicar Migration de Geolocalização

**⚠️ ATENÇÃO**: Este passo é opcional! Só faça se quiser salvar as coordenadas no banco.

### Passo 1: Backup do banco de dados
```bash
python manage.py dumpdata > backup_antes_migracao.json
```

### Passo 2: Editar o modelo
Abra `core/models.py` e adicione ao modelo `RegistroPonto`:

```python
latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
```

### Passo 3: Criar migration
```bash
python manage.py makemigrations
```

### Passo 4: Aplicar migration
```bash
python manage.py migrate
```

**Veja o guia completo em**: [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md)

---

## 4️⃣ Testar em Desenvolvimento

```bash
python manage.py runserver
```

Acesse: `http://localhost:8000`

**Teste:**
1. Vá para Dashboard
2. Veja o banner "Recursos PWA Disponíveis"
3. Clique nos 3 botões de teste

---

## 5️⃣ Deploy em Produção (Linux)

### Passo 1: Conectar ao servidor
```bash
ssh usuario@seu-servidor.com
```

### Passo 2: Ir para o projeto
```bash
cd /home/usuario/blockline_app
```

### Passo 3: Ativar ambiente virtual
```bash
source venv/bin/activate
```

### Passo 4: Pull do código
```bash
git pull origin main
```

Ou se não usar git, faça upload via FTP/SCP dos arquivos:
- `core/static/pwa-*.js` (3 arquivos)
- `core/templates/core/*.html` (3 arquivos modificados)

### Passo 5: Coletar estáticos
```bash
cd blockline_app
python manage.py collectstatic --noinput
```

### Passo 6: (Opcional) Aplicar migrations
```bash
python manage.py migrate
```

### Passo 7: Reiniciar servidor
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

Ou:
```bash
sudo supervisorctl restart blockline
```

---

## 6️⃣ Verificar em Produção

1. Acesse via HTTPS: `https://picsart.com.br`
2. Abra o console (F12)
3. Veja se os scripts carregaram:
   ```
   🔔 Sistema de notificações carregado
   📸 Sistema de câmera carregado
   📍 Sistema de geolocalização carregado
   ```

---

## 🎯 Checklist Rápido

```bash
# DEV
[ ] Ativar venv
[ ] collectstatic
[ ] runserver
[ ] Testar dashboard
[ ] Testar notificações
[ ] Testar scanner
[ ] Testar geolocalização

# PROD
[ ] Backup do banco
[ ] Pull código / Upload arquivos
[ ] Ativar venv
[ ] collectstatic
[ ] (Opcional) migrate
[ ] Reiniciar servidor
[ ] Testar em HTTPS
```

---

## 🐛 Se der erro

### Erro: "No module named 'django'"
**Solução**: Ative o ambiente virtual primeiro
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Erro: "Static files not found"
**Solução**: Execute collectstatic
```bash
python manage.py collectstatic --noinput
```

### Erro: 404 nos scripts PWA
**Solução**:
1. Verifique se os arquivos existem em `core/static/`
2. Execute `collectstatic`
3. Verifique o caminho em `base.html` (deve usar `{% static %}`)

### Erro: "Permission denied" no servidor
**Solução**:
```bash
# Dar permissão aos arquivos
sudo chown -R www-data:www-data /caminho/do/projeto/static
sudo chmod -R 755 /caminho/do/projeto/static
```

---

## 📞 Comandos Úteis

### Ver logs do servidor
```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Verificar status
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### Limpar cache do Django
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
>>> exit()
```

---

## 🎉 Pronto!

Depois destes comandos, o sistema estará com todas as funcionalidades PWA ativas:
- ✅ Notificações Push
- ✅ Scanner de Câmera
- ✅ Geolocalização

**Próximo passo**: Treinar os usuários a ativar as permissões!

---

**Versão**: 2.0.0 - PWA Fase 2
**Data**: Outubro 2025
