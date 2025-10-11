# 🔄 Guia de Migração - Adicionar Geolocalização ao Ponto

## 📋 Objetivo

Adicionar campos de latitude e longitude ao modelo `RegistroPonto` para armazenar a localização onde o ponto foi batido.

## 🛠️ Passo a Passo

### 1. Atualizar o Modelo

Edite o arquivo `core/models.py` e adicione os campos ao modelo `RegistroPonto`:

```python
# core/models.py

class RegistroPonto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('inicio_almoco', 'Início Almoço'),
        ('fim_almoco', 'Fim Almoço'),
    ])
    data_hora = models.DateTimeField(auto_now_add=True)

    # 🆕 NOVOS CAMPOS - Adicione estas linhas
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Latitude GPS do local onde o ponto foi registrado'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Longitude GPS do local onde o ponto foi registrado'
    )

    class Meta:
        verbose_name = 'Registro de Ponto'
        verbose_name_plural = 'Registros de Ponto'
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
```

### 2. Criar a Migration

Execute o comando para criar a migration:

```bash
python manage.py makemigrations
```

Você verá algo como:
```
Migrations for 'core':
  core/migrations/0XXX_add_location_to_registroponto.py
    - Add field latitude to registroponto
    - Add field longitude to registroponto
```

### 3. Aplicar a Migration

Execute o comando para aplicar as mudanças no banco de dados:

```bash
python manage.py migrate
```

Você verá algo como:
```
Operations to perform:
  Apply all migrations: core
Running migrations:
  Applying core.0XXX_add_location_to_registroponto... OK
```

### 4. Atualizar a View

Edite o arquivo `core/views.py` e modifique a view `bater_ponto` para salvar as coordenadas:

```python
# core/views.py

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def bater_ponto(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        latitude = request.POST.get('latitude')  # 🆕
        longitude = request.POST.get('longitude')  # 🆕

        try:
            ponto = RegistroPonto.objects.create(
                usuario=request.user,
                tipo=tipo,
                data_hora=timezone.now(),
                latitude=latitude if latitude else None,  # 🆕
                longitude=longitude if longitude else None  # 🆕
            )

            tipo_display = dict(RegistroPonto._meta.get_field('tipo').choices)[tipo]

            # Mensagem de sucesso com localização (se disponível)
            if latitude and longitude:
                messages.success(
                    request,
                    f'✅ {tipo_display} registrado com sucesso! 📍 Localização: {latitude}, {longitude}'
                )
            else:
                messages.success(
                    request,
                    f'✅ {tipo_display} registrado com sucesso!'
                )

        except Exception as e:
            messages.error(request, f'❌ Erro ao registrar ponto: {str(e)}')

        return redirect('controle_ponto')

    return redirect('controle_ponto')
```

### 5. (Opcional) Atualizar o Admin

Para visualizar as coordenadas no Django Admin:

```python
# core/admin.py

from django.contrib import admin
from .models import RegistroPonto

@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario',
        'tipo',
        'data_hora',
        'latitude',
        'longitude',
        'ver_no_mapa'  # 🆕
    ]
    list_filter = ['tipo', 'data_hora', 'usuario']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name']
    readonly_fields = ['data_hora', 'latitude', 'longitude']

    # 🆕 Link para ver no Google Maps
    def ver_no_mapa(self, obj):
        if obj.latitude and obj.longitude:
            url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html(
                '<a href="{}" target="_blank">🗺️ Ver no Mapa</a>',
                url
            )
        return '-'

    ver_no_mapa.short_description = 'Localização'

from django.utils.html import format_html  # Adicione no topo do arquivo
```

### 6. (Opcional) Criar View de Relatório de Localização

Crie uma view para visualizar os locais onde os pontos foram batidos:

```python
# core/views.py

@login_required
def mapa_pontos(request):
    """Exibir mapa com todos os pontos registrados"""
    pontos = RegistroPonto.objects.filter(
        usuario=request.user,
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('-data_hora')[:30]  # Últimos 30 pontos

    context = {
        'pontos': pontos
    }

    return render(request, 'core/mapa_pontos.html', context)
```

E crie o template `core/templates/core/mapa_pontos.html`:

```html
{% extends 'core/base.html' %}

{% block content %}
<div class="max-w-7xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 mb-6">🗺️ Mapa de Pontos</h1>

    <!-- Lista de pontos -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h2 class="text-xl font-bold mb-4">Últimos 30 Registros</h2>

        <div class="space-y-3">
            {% for ponto in pontos %}
            <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                    <p class="font-semibold">{{ ponto.get_tipo_display }}</p>
                    <p class="text-sm text-gray-600">{{ ponto.data_hora|date:'d/m/Y H:i' }}</p>
                    <p class="text-xs text-gray-500">
                        📍 {{ ponto.latitude }}, {{ ponto.longitude }}
                    </p>
                </div>
                <a href="https://www.google.com/maps?q={{ ponto.latitude }},{{ ponto.longitude }}"
                   target="_blank"
                   class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                    🗺️ Ver no Mapa
                </a>
            </div>
            {% empty %}
            <p class="text-gray-400 text-center py-8">Nenhum ponto com localização registrada</p>
            {% endfor %}
        </div>
    </div>

    <!-- Mapa (opcional - requer API do Google Maps) -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 class="text-xl font-bold mb-4">Mapa Interativo</h2>
        <div id="map" class="w-full h-96 rounded-lg bg-gray-100"></div>
        <p class="text-sm text-gray-500 mt-2">
            💡 Para exibir o mapa, integre com Google Maps API
        </p>
    </div>
</div>
{% endblock %}
```

Adicione a URL em `core/urls.py`:

```python
# core/urls.py

urlpatterns = [
    # ... outras URLs ...
    path('ponto/mapa/', mapa_pontos, name='mapa_pontos'),
]
```

---

## ✅ Checklist

- [ ] Atualizar modelo `RegistroPonto`
- [ ] Criar migration (`makemigrations`)
- [ ] Aplicar migration (`migrate`)
- [ ] Atualizar view `bater_ponto`
- [ ] (Opcional) Atualizar Django Admin
- [ ] (Opcional) Criar view de mapa
- [ ] Testar no ambiente de desenvolvimento
- [ ] Fazer backup do banco antes de migrar em produção
- [ ] Aplicar em produção

---

## 🧪 Testar

### Teste Manual

1. Acesse o controle de ponto
2. Bata um ponto (permita acesso à localização)
3. Verifique no Django Admin se as coordenadas foram salvas
4. Acesse o mapa de pontos (se criou a view opcional)

### Teste via Shell

```bash
python manage.py shell
```

```python
from core.models import RegistroPonto

# Ver últimos pontos com localização
pontos = RegistroPonto.objects.filter(
    latitude__isnull=False,
    longitude__isnull=False
).order_by('-data_hora')[:5]

for p in pontos:
    print(f"{p.usuario.username} - {p.tipo} - {p.latitude},{p.longitude}")
```

---

## 🔄 Rollback (em caso de problemas)

Se algo der errado, você pode reverter a migration:

```bash
# Ver número da migration anterior
python manage.py showmigrations core

# Reverter para migration anterior
python manage.py migrate core 0XXX_migration_anterior
```

---

## 📊 Análise de Dados (Opcional)

Após coletar dados de localização, você pode fazer análises interessantes:

```python
# Descobrir o local mais comum de batida de ponto
from django.db.models import Count
from core.models import RegistroPonto

pontos_comuns = RegistroPonto.objects.filter(
    latitude__isnull=False
).values('latitude', 'longitude').annotate(
    total=Count('id')
).order_by('-total')[:5]

for p in pontos_comuns:
    print(f"Local: {p['latitude']},{p['longitude']} - {p['total']} registros")
```

---

## 🚀 Deploy em Produção

### Antes do Deploy

1. **Backup do banco de dados**:
```bash
python manage.py dumpdata > backup_antes_migracao.json
```

2. **Teste em ambiente de staging primeiro**

### Durante o Deploy

```bash
# 1. Pull do código
git pull origin main

# 2. Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependências (se houver)
pip install -r requirements.txt

# 4. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 5. Aplicar migrations
python manage.py migrate

# 6. Reiniciar servidor
sudo systemctl restart gunicorn  # ou seu servidor
```

---

**Implementado**: Outubro 2025
**Versão**: 2.0.0
