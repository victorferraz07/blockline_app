# Instruções de Configuração - Sistema de Requisições Melhorado

## ✅ Mudanças Implementadas

### 1. Models Atualizados

**PerfilUsuario** ([core/models.py](core/models.py)):
- ✅ Adicionado campo `is_financeiro` (BooleanField)

**RequisicaoCompra** ([core/models.py](core/models.py)):
- ✅ Adicionado `link_item` (URLField)
- ✅ Adicionado `forma_pagamento` (CharField com choices: pix, dinheiro, transferencia_bancaria, boleto, cartao)
- ✅ Adicionado campos específicos para boleto:
  - `quantidade_parcelas` (IntegerField)
  - `dias_pagamento` (TextField)
  - `documento_boleto` (FileField)
  - `dias_aviso_pagamento` (IntegerField, default=3)
- ✅ Adicionado `documento_nota_fiscal` (FileField)

### 2. Views Atualizadas

**criar_requisicao** ([core/views.py](core/views.py)):
- ✅ Captura campo `link_item`

**aprovar_requisicao** ([core/views.py](core/views.py)):
- ✅ Removido upload de `documento_aprovacao`

**marcar_como_comprado** ([core/views.py](core/views.py)):
- ✅ Captura `forma_pagamento`
- ✅ Captura campos específicos de boleto (quando aplicável)
- ✅ Upload de `documento_boleto` (opcional)
- ✅ Upload de `documento_nota_fiscal` (opcional)

**editar_requisicao** ([core/views.py](core/views.py)):
- ✅ Suporte completo para todos os novos campos
- ✅ Rastreamento de mudanças no histórico

### 3. Templates Atualizados

**Modal "Nova Compra"** ([core/templates/core/lista_requisicoes.html](core/templates/core/lista_requisicoes.html)):
- ✅ Adicionado "rolo" ao select de unidade
- ✅ Adicionado campo `link_item` (URL)

**Form de Aprovação**:
- ✅ Removido campo de upload de documento

**Form "Marcar como Comprado"**:
- ✅ Adicionado select de `forma_pagamento`
- ✅ Campos condicionais para boleto (aparecem apenas quando forma_pagamento='boleto'):
  - Quantidade de parcelas
  - Dias de pagamento
  - Dias de antecedência para aviso
  - Upload de documento do boleto
- ✅ Upload de nota fiscal (para todas as formas de pagamento)

**Form de Edição**:
- ✅ Adicionado "rolo" ao select de unidade
- ✅ Adicionado campo `link_item`

### 4. Django Admin Atualizado

**PerfilUsuarioInline** ([core/admin.py](core/admin.py)):
- ✅ Campo `is_financeiro` disponível para edição

### 5. Configurações de Email

**settings.py** ([config/settings.py](config/settings.py)):
- ✅ Configurações SMTP adicionadas (Gmail)

**.env** ([.env](.env)):
- ✅ Variáveis de email adicionadas (valores placeholder)

### 6. Management Command

**verificar_boletos_vencimento.py** ([core/management/commands/verificar_boletos_vencimento.py](core/management/commands/verificar_boletos_vencimento.py)):
- ✅ Verifica boletos próximos do vencimento
- ✅ Envia alertas por email para usuários com `is_financeiro=True`
- ✅ Suporta múltiplos vencimentos (ex: "15, 30, 45")
- ✅ Trata casos especiais (dia 31 em mês com 30 dias)

---

## 🔧 Próximos Passos (VOCÊ DEVE EXECUTAR)

### Passo 1: Resolver Problema de Codificação do Banco de Dados

Há um erro de codificação UTF-8 na conexão com o PostgreSQL. Verifique:

1. Abra o arquivo `.env` e certifique-se de que não há caracteres especiais nas configurações do banco
2. Se o problema persistir, verifique as configurações do PostgreSQL

### Passo 2: Executar Migrations

Após resolver o problema de codificação, execute:

```bash
cd /caminho/do/projeto
source venv/bin/activate  # ou venv\Scripts\activate no Windows
python manage.py makemigrations
python manage.py migrate
```

### Passo 3: Configurar Email (Gmail)

1. Acesse: https://myaccount.google.com/apppasswords
2. Crie uma senha de aplicativo para "Mail"
3. Edite o arquivo `.env` e substitua os valores:

```env
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app_gerada_aqui
DEFAULT_FROM_EMAIL=noreply@picsart.com.br
```

### Passo 4: Marcar Usuários como Financeiro

1. Acesse o Django Admin: `https://picsart.com.br/blockline/admin/`
2. Vá em "Usuários"
3. Edite o usuário que deve receber alertas
4. Na seção "Perfil do Usuário", marque o campo **"É do Financeiro"**
5. Salve

### Passo 5: Testar o Management Command

Execute manualmente para testar:

```bash
python manage.py verificar_boletos_vencimento
```

**Esperado:**
- Se não houver boletos: "Verificação concluída. 0 alerta(s) enviado(s)."
- Se houver boletos vencendo: Emails enviados para usuários do financeiro

### Passo 6: Configurar Cron Job (Linux/Unix)

Como você está usando Linux/Unix, configure o cron job:

```bash
crontab -e
```

Adicione a linha (substitua os caminhos):

```cron
0 9 * * * cd /caminho/completo/do/projeto && /caminho/completo/do/venv/bin/python manage.py verificar_boletos_vencimento
```

**Exemplo:**
```cron
0 9 * * * cd /home/usuario/django_user/blockline_app && /home/usuario/django_user/blockline_app/venv/bin/python manage.py verificar_boletos_vencimento
```

Isso executará a verificação **diariamente às 9h da manhã**.

Para testar se o cron está funcionando, você pode temporariamente mudar para executar a cada minuto:

```cron
* * * * * cd /caminho/do/projeto && /caminho/do/venv/bin/python manage.py verificar_boletos_vencimento
```

Depois de confirmar que funciona, volte para `0 9 * * *`.

### Passo 7: Criar Diretórios de Upload

Certifique-se de que os diretórios de upload existem:

```bash
mkdir -p media/requisicoes/boletos
mkdir -p media/requisicoes/notas_fiscais
chmod 755 media/requisicoes/boletos
chmod 755 media/requisicoes/notas_fiscais
```

---

## 📝 Como Usar as Novas Funcionalidades

### Criar Nova Requisição com Link

1. Clique em "➕ Nova Compra"
2. Preencha os campos (agora com opção "rolo" em Unidade)
3. Cole o link do produto no campo "Link do Item"
4. Submeta

### Aprovar Requisição

1. Na seção "Pendentes", clique em "✅ Aprovar"
2. Adicione observação (opcional)
3. **Não há mais upload de documento nesta etapa**

### Marcar como Comprado

1. Na seção "Aprovados", clique em "🛒 Marcar como Comprado"
2. Preencha preço real e fornecedor
3. Selecione **Forma de Pagamento**
4. **Se selecionar "Boleto":**
   - Preencha quantidade de parcelas
   - Informe dias de pagamento (ex: "15, 30, 45")
   - Defina dias de antecedência para aviso (padrão: 3)
   - Faça upload do documento do boleto (opcional)
5. Faça upload da nota fiscal (opcional)
6. Confirme

### Alertas Automáticos de Boleto

- O sistema envia email automaticamente quando um boleto está próximo do vencimento
- Os alertas são enviados com a antecedência configurada (campo "Dias de Antecedência para Aviso")
- **Exemplo:** Se configurado para 3 dias e vencimento é dia 15, o alerta será enviado nos dias 12, 13, 14 e 15
- Apenas usuários com `is_financeiro=True` recebem os alertas

---

## 🧪 Testes Recomendados

### Teste 1: Nova Requisição com Link e "Rolo"
1. Criar requisição com unidade="rolo" e link_item preenchido
2. Verificar que aparece corretamente na lista

### Teste 2: Aprovação Sem Documento
1. Aprovar uma requisição pendente
2. Confirmar que não há opção de upload

### Teste 3: Compra com Boleto
1. Marcar requisição como comprada
2. Selecionar forma_pagamento="boleto"
3. Verificar que campos de boleto aparecem dinamicamente
4. Preencher dados de boleto e fazer upload de documentos
5. Confirmar salvamento

### Teste 4: Compra com PIX (sem boleto)
1. Marcar requisição como comprada
2. Selecionar forma_pagamento="pix"
3. Verificar que campos de boleto NÃO aparecem
4. Fazer upload apenas de nota fiscal

### Teste 5: Alerta de Boleto
1. Criar requisição com boleto vencendo em 3 dias
2. Executar: `python manage.py verificar_boletos_vencimento`
3. Verificar email recebido pelo usuário financeiro

---

## 🚨 Problemas Conhecidos

### Erro de Codificação UTF-8 no PostgreSQL

**Sintoma:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe7 in position 78
```

**Solução:**
1. Verifique o arquivo `.env` (não deve ter caracteres especiais)
2. Verifique encoding do PostgreSQL: `SHOW client_encoding;`
3. Se necessário, ajuste: `SET client_encoding = 'UTF8';`

---

## 📄 Arquivos Modificados

- [core/models.py](core/models.py) - Linhas 18-27, 523-582
- [core/views.py](core/views.py) - Linhas 2110-2127, 2275-2298, 2352-2382, 2132-2270
- [core/templates/core/lista_requisicoes.html](core/templates/core/lista_requisicoes.html)
- [core/admin.py](core/admin.py) - Linha 24
- [config/settings.py](config/settings.py) - Após linha 107
- [.env](.env) - Variáveis de email adicionadas

## 📄 Arquivos Criados

- [core/management/commands/verificar_boletos_vencimento.py](core/management/commands/verificar_boletos_vencimento.py)
- [INSTRUCOES_REQUISICOES.md](INSTRUCOES_REQUISICOES.md) (este arquivo)

---

## 🎯 Resultado Final

✅ Unidade "rolo" disponível
✅ Campo de link em requisições
✅ Aprovação sem upload de documento
✅ Controle completo de formas de pagamento
✅ Dados específicos para boletos (parcelas, vencimentos)
✅ Upload de documentos de boleto e nota fiscal
✅ Perfil financeiro para usuários
✅ Alertas automáticos por email para boletos vencendo
✅ Execução diária às 9h via Cron Job

**Benefício:** Controle financeiro aprimorado com rastreamento de boletos e alertas automáticos, reduzindo risco de pagamentos atrasados.
