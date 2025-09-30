from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Empresa, PerfilUsuario, Setor, Fornecedor, 
    ItemFornecedor, ItemEstoque, Recebimento, 
    ImagemItemEstoque, ProdutoFabricado, DocumentoProdutoFabricado, 
    ImagemProdutoFabricado, Componente, Expedicao, 
    ItemExpedido, DocumentoExpedicao, ImagemExpedicao
)

# --- Configurações de Administração Customizadas ---

# 1. Crie uma classe 'inline' para o Perfil
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário'
    # 'filter_horizontal' melhora a seleção de ManyToManyField
    filter_horizontal = ('empresas_permitidas',)

# 2. Crie uma nova classe de Admin para o Usuário que usa o inline
class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)

# 3. Cancele o registro padrão do User e registre novamente com nossa versão customizada
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    # CORREÇÃO AQUI: Removemos o filtro inválido 'empresa__nome'
    # e mantivemos os que funcionam.
    list_display = ('nome', 'quantidade', 'local_armazenamento', 'data_atualizacao', 'tipo')
    search_fields = ('nome', 'descricao', 'local_armazenamento')
    list_filter = ('tipo', 'data_atualizacao', 'data_criacao')
    
    # Função para mostrar a empresa de forma segura
    def empresa_associada(self, obj):
        if obj.is_produto_fabricado and hasattr(obj, 'receita'):
            return obj.receita.empresa
        return None
    empresa_associada.short_description = 'Empresa (se Produto)'


# --- Registros Simples ---
admin.site.register(Empresa)
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