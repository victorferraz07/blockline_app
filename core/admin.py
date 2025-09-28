# core/admin.py
from django.contrib import admin
from .models import (
    ItemEstoque, ProdutoFabricado, Recebimento, 
    DocumentoProdutoFabricado, Componente, Setor, Fornecedor,
    ImagemProdutoFabricado, ImagemItemEstoque, ItemFornecedor,
    Expedicao, ItemExpedido, DocumentoExpedicao, ImagemExpedicao, Empresa, PerfilUsuario
)

@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'local_armazenamento', 'data_atualizacao')
    search_fields = ('nome', 'descricao', 'local_armazenamento')
    list_filter = ('data_atualizacao', 'data_criacao')

# Registrando todos os outros
admin.site.register(Empresa)
admin.site.register(PerfilUsuario)
admin.site.register(Setor)
admin.site.register(Fornecedor)
admin.site.register(ItemFornecedor)
admin.site.register(Recebimento)
admin.site.register(ImagemItemEstoque)
admin.site.register(ProdutoFabricado)
admin.site.register(DocumentoProdutoFabricado)
admin.site.register(ImagemProdutoFabricado)
admin.site.register(Componente)
admin.site.register(Expedicao)
admin.site.register(ItemExpedido)
admin.site.register(DocumentoExpedicao)
admin.site.register(ImagemExpedicao)