# core/admin.py

from django.contrib import admin
# Importe todos os modelos que criamos no models.py
from .models import Setor, ItemEstoque, ProdutoFabricado, Componente, Recebimento, SaidaProduto

# --- Uma pitada de customização para o ItemEstoque ---
# Esta classe nos permite customizar como o modelo é exibido no admin.
@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    # 'list_display' define quais colunas aparecerão na lista de itens.
    list_display = ('nome', 'quantidade', 'local_armazenamento', 'data_atualizacao')
    # 'search_fields' cria uma barra de pesquisa que busca nos campos definidos.
    search_fields = ('nome', 'descricao', 'local_armazenamento')
    # 'list_filter' cria um filtro na barra lateral.
    list_filter = ('data_atualizacao', 'data_criacao')

# Registrando os outros modelos da forma mais simples.
# O Django criará uma interface padrão para eles.
admin.site.register(Setor)
admin.site.register(ProdutoFabricado)
admin.site.register(Componente)
admin.site.register(Recebimento)
admin.site.register(SaidaProduto)