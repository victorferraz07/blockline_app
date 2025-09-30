from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Empresa, PerfilUsuario, Setor, Fornecedor,
    ItemFornecedor, ItemEstoque, Recebimento,
    ImagemItemEstoque, ProdutoFabricado, DocumentoProdutoFabricado,
    ImagemProdutoFabricado, Componente, Expedicao,
    ItemExpedido, DocumentoExpedicao, ImagemExpedicao,
    KanbanColumn, Task, TaskQuantidadeFeita, TaskHistorico,
    JornadaTrabalho, RegistroPonto, ResumoMensal
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

# --- Registros Kanban ---
@admin.register(KanbanColumn)
class KanbanColumnAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor', 'ordem')
    list_editable = ('ordem',)
    ordering = ('ordem',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'coluna', 'quantidade_meta', 'get_quantidade_produzida', 'em_andamento', 'finalizado', 'criado_em')
    list_filter = ('coluna', 'em_andamento', 'finalizado', 'criado_em')
    search_fields = ('titulo', 'descricao')
    filter_horizontal = ('responsaveis',)
    readonly_fields = ('criado_em', 'atualizado_em')

    def get_quantidade_produzida(self, obj):
        return obj.quantidade_produzida
    get_quantidade_produzida.short_description = 'Produzida'

@admin.register(TaskHistorico)
class TaskHistoricoAdmin(admin.ModelAdmin):
    list_display = ('task', 'tipo_acao', 'usuario', 'data')
    list_filter = ('tipo_acao', 'data')
    search_fields = ('task__titulo', 'descricao')
    readonly_fields = ('task', 'usuario', 'tipo_acao', 'descricao', 'data')

admin.site.register(TaskQuantidadeFeita)

# --- Registros de Ponto ---
@admin.register(JornadaTrabalho)
class JornadaTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'horas_diarias', 'dias_semana')
    search_fields = ('usuario__username',)

@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'data_hora', 'localizacao')
    list_filter = ('tipo', 'data_hora')
    search_fields = ('usuario__username',)
    readonly_fields = ('data_hora',)

@admin.register(ResumoMensal)
class ResumoMensalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mes', 'ano', 'horas_trabalhadas', 'horas_esperadas', 'saldo_horas')
    list_filter = ('mes', 'ano')
    search_fields = ('usuario__username',)