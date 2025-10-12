# 🔍 COMO VER OS LOGS DO ERRO NO SERVIDOR

## ✅ PROGRESSO: A página não está mais crashando!

Agora você está vendo a mensagem:
```
"Erro ao carregar dashboard. Por favor, contate o administrador."
```

Isso significa que o **try-except está funcionando** e capturando o erro!

Agora precisamos ver **qual é o erro exato** para corrigi-lo.

---

## 📋 COMANDOS PARA VER O ERRO NOS LOGS

### **1. Conectar ao Servidor**
```bash
ssh usuario@picsart.com.br
```

---

### **2. Ver Últimos Logs do Gunicorn**

#### **Opção A: Ver últimas 100 linhas (Recomendado)**
```bash
sudo journalctl -u gunicorn -n 100 --no-pager
```

#### **Opção B: Ver logs em tempo real**
```bash
sudo journalctl -u gunicorn -f
```
(Depois acesse o dashboard no navegador e veja o erro aparecer em tempo real)

#### **Opção C: Filtrar apenas erros (ERROR)**
```bash
sudo journalctl -u gunicorn | grep -i "ERROR" | tail -50
```

#### **Opção D: Ver logs das últimas 10 minutos**
```bash
sudo journalctl -u gunicorn --since "10 minutes ago"
```

---

### **3. Procurar Especificamente pelo Erro do Dashboard**

```bash
sudo journalctl -u gunicorn | grep -A 20 "Erro no dashboard"
```

Isso mostrará o erro e as 20 linhas seguintes (que incluem o traceback completo).

---

### **4. Se Usar Nginx, Ver Logs do Nginx Também**

```bash
# Ver últimas linhas do erro log
sudo tail -n 100 /var/log/nginx/error.log

# Ou em tempo real
sudo tail -f /var/log/nginx/error.log
```

---

### **5. Ver Logs do Django Diretamente (se configurado)**

```bash
# Procurar pelo arquivo de log
find /caminho/do/projeto -name "*.log" 2>/dev/null

# Ver o conteúdo
tail -n 100 /caminho/do/projeto/logs/django.log
```

---

## 🎯 O QUE PROCURAR NOS LOGS

Você vai ver algo parecido com isto:

```
ERROR - Erro no dashboard: <DESCRIÇÃO DO ERRO AQUI>
Traceback (most recent call last):
  File "/caminho/core/views.py", line X, in dashboard
    <linha de código que causou o erro>
  <tipo de erro>: <mensagem do erro>
```

---

## 📝 EXEMPLOS DE ERROS COMUNS E O QUE SIGNIFICAM

### **Erro 1: DoesNotExist**
```
Empresa.DoesNotExist: Empresa matching query does not exist
```
**Solução:** Criar uma empresa no banco
```bash
python manage.py shell
>>> from core.models import Empresa
>>> Empresa.objects.create(nome="Picsart", acesso_liberado=True)
>>> exit()
```

---

### **Erro 2: OperationalError - no such table**
```
OperationalError: no such table: core_empresa
```
**Solução:** Rodar migrations
```bash
python manage.py migrate
```

---

### **Erro 3: AttributeError**
```
AttributeError: 'NoneType' object has no attribute 'pk'
```
**Solução:** Algum objeto está None quando não deveria. Precisamos ver qual linha do código.

---

### **Erro 4: FieldError**
```
FieldError: Cannot resolve keyword 'empresa' into field
```
**Solução:** Algum modelo não tem o campo 'empresa'. Precisamos ajustar o filtro.

---

### **Erro 5: ProgrammingError**
```
ProgrammingError: column core_recebimento.empresa_id does not exist
```
**Solução:** Migrations pendentes ou banco desatualizado
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🔧 DEPOIS DE IDENTIFICAR O ERRO

**Me envie:**
1. O erro completo (a linha que começa com ERROR)
2. O traceback (as linhas que mostram o caminho do erro)
3. O tipo de exceção (ex: DoesNotExist, OperationalError, etc)

**Com essas informações, posso criar a correção exata!**

---

## 💡 COMANDO RÁPIDO PARA COPIAR E COLAR

```bash
# Um único comando que mostra tudo que precisamos:
echo "=== LOGS DO GUNICORN ===" && \
sudo journalctl -u gunicorn | grep -A 30 "Erro no dashboard" | tail -50 && \
echo "" && \
echo "=== VERIFICANDO EMPRESAS ===" && \
python manage.py shell -c "from core.models import Empresa; print(f'Total de empresas: {Empresa.objects.count()}')"
```

---

## 📞 ATALHOS ÚTEIS

### **Reiniciar serviços:**
```bash
sudo systemctl restart gunicorn nginx
```

### **Ver status:**
```bash
sudo systemctl status gunicorn
```

### **Ver processos Python rodando:**
```bash
ps aux | grep python
```

### **Ver porta 8000 em uso:**
```bash
sudo netstat -tlnp | grep 8000
```

---

## ✅ CHECKLIST

Execute no servidor:

```bash
# 1. Ver logs recentes
sudo journalctl -u gunicorn -n 100 --no-pager | grep -A 20 "ERROR"

# 2. Verificar empresas
cd /caminho/do/projeto
source venv/bin/activate
python manage.py shell -c "from core.models import Empresa; print(f'Empresas: {Empresa.objects.count()}')"

# 3. Verificar versão do código
git log --oneline -1

# 4. Copiar e me enviar o erro completo
```

---

**PRÓXIMO PASSO:** Execute os comandos acima e me envie o erro que aparecer nos logs!
