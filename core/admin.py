# core/admin.py
from django.contrib import admin
from .models import (
    Setor, 
    ItemEstoque, 
    ProdutoFabricado, 
    Componente, 
    Recebimento, 
    SaidaProduto,
    ImagemItemEstoque,
    ImagemProdutoFabricado,
    DocumentoProdutoFabricado
)

@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'local_armazenamento', 'data_atualizacao')
    search_fields = ('nome', 'descricao', 'local_armazenamento')
    list_filter = ('data_atualizacao', 'data_criacao')

# Registrando todos os outros
admin.site.register(Setor)
admin.site.register(ProdutoFabricado)
admin.site.register(Componente)
admin.site.register(Recebimento)
admin.site.register(SaidaProduto)
admin.site.register(ImagemItemEstoque)
admin.site.register(ImagemProdutoFabricado)
admin.site.register(DocumentoProdutoFabricado)