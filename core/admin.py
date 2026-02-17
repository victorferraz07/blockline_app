from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Empresa, PerfilUsuario, Setor, Fornecedor, Cliente,
    ItemFornecedor, ItemEstoque, Recebimento,
    ImagemItemEstoque, ProdutoFabricado, DocumentoProdutoFabricado,
    ImagemProdutoFabricado, Componente, Expedicao,
    ItemExpedido, DocumentoExpedicao, ImagemExpedicao,
    JornadaTrabalho, RegistroPonto, ResumoMensal, AbonoDia,
    MovimentacaoEstoque, RequisicaoCompra, HistoricoRequisicao,
    GastoViagem, GastoCaixaInterno,
    Project, Milestone, Sprint, Label, ProjectTask, ProjectAutomation, TaskQuantidadeFeita, TaskHistorico,
    Notificacao
)

# --- Configurações de Administração Customizadas ---

# 1. Crie uma classe 'inline' para o Perfil
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário'
    # 'filter_horizontal' melhora a seleção de ManyToManyField
    filter_horizontal = ('empresas_permitidas',)
    fields = ('empresas_permitidas', 'is_financeiro')

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
admin.site.register(ItemFornecedor)
admin.site.register(ImagemItemEstoque)

@admin.register(Recebimento)
class RecebimentoAdmin(admin.ModelAdmin):
    list_display = ('numero_nota_fiscal', 'fornecedor', 'get_nome_fornecedor', 'setor', 'valor_total', 'status', 'data_recebimento', 'usuario')
    list_filter = ('status', 'data_recebimento', 'setor')
    search_fields = ('numero_nota_fiscal', 'fornecedor__nome', 'fornecedor_nome', 'observacoes')
    readonly_fields = ('data_recebimento',)
    exclude = ('empresa',)  # Ocultar campo empresa

    def get_nome_fornecedor(self, obj):
        return obj.get_nome_fornecedor()
    get_nome_fornecedor.short_description = 'Nome Fornecedor'
admin.site.register(ProdutoFabricado)
admin.site.register(DocumentoProdutoFabricado)
admin.site.register(ImagemProdutoFabricado)
admin.site.register(Componente)
@admin.register(Expedicao)
class ExpedicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'nota_fiscal', 'usuario', 'data_expedicao')
    list_filter = ('data_expedicao',)
    search_fields = ('cliente', 'nota_fiscal', 'observacoes')
    readonly_fields = ('data_expedicao',)
    exclude = ('empresa',)  # Ocultar campo empresa
admin.site.register(ItemExpedido)
admin.site.register(DocumentoExpedicao)
admin.site.register(ImagemExpedicao)

# --- Registros de Ponto ---
@admin.register(JornadaTrabalho)
class JornadaTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'horas_diarias', 'horas_sexta', 'intervalo_almoco', 'dias_semana', 'periodo_mes_display')
    search_fields = ('usuario__username',)
    fieldsets = (
        ('Usuário', {'fields': ('usuario',)}),
        ('Horários', {'fields': ('horas_diarias', 'horas_sexta', 'intervalo_almoco')}),
        ('Dias da Semana', {'fields': ('dias_semana',)}),
        ('Período do Mês', {'fields': ('dia_inicio_mes', 'dia_fim_mes'), 'description': 'Configure o período de cálculo mensal. Use 0 para "último dia do mês".'}),
    )

    def periodo_mes_display(self, obj):
        if obj.dia_inicio_mes == 1 and obj.dia_fim_mes == 0:
            return 'Padrão (1 ao último)'
        elif obj.dia_fim_mes == 0:
            return f'Dia {obj.dia_inicio_mes} ao último'
        else:
            return f'Dia {obj.dia_inicio_mes} ao {obj.dia_fim_mes}'
    periodo_mes_display.short_description = 'Período do Mês'

@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'data_hora', 'abonado', 'abonado_por', 'localizacao')
    list_filter = ('tipo', 'abonado', 'data_hora')
    search_fields = ('usuario__username',)
    readonly_fields = ('data_hora',)

@admin.register(AbonoDia)
class AbonoDiaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data', 'tipo_abono', 'horas_abonadas', 'abonado_por', 'data_criacao')
    list_filter = ('tipo_abono', 'data', 'data_criacao')
    search_fields = ('usuario__username', 'motivo')
    readonly_fields = ('data_criacao',)
    fieldsets = (
        ('Informações do Funcionário', {'fields': ('usuario', 'data')}),
        ('Detalhes do Abono', {'fields': ('tipo_abono', 'horas_abonadas', 'motivo')}),
        ('Aprovação', {'fields': ('abonado_por', 'data_criacao')}),
    )

@admin.register(ResumoMensal)
class ResumoMensalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mes', 'ano', 'horas_trabalhadas', 'horas_esperadas', 'saldo_horas')
    list_filter = ('mes', 'ano')
    search_fields = ('usuario__username',)

# --- Registro de Movimentações de Estoque ---
@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('item', 'tipo', 'quantidade', 'usuario', 'data_hora')
    list_filter = ('tipo', 'data_hora')
    search_fields = ('item__nome', 'observacoes', 'usuario__username')
    readonly_fields = ('item', 'tipo', 'quantidade', 'usuario', 'data_hora', 'observacoes')
    date_hierarchy = 'data_hora'
    ordering = ('-data_hora',)

    def has_add_permission(self, request):
        # Não permitir adição manual - movimentações são criadas automaticamente
        return False

    def has_change_permission(self, request, obj=None):
        # Não permitir edição - é um histórico
        return False

    def has_delete_permission(self, request, obj=None):
        # Permitir exclusão apenas para superusuários
        return request.user.is_superuser

# --- Admin para Cliente e Fornecedor ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'mercado', 'data_cadastro')
    list_filter = ('mercado', 'data_cadastro')
    search_fields = ('nome', 'email', 'telefone')
    filter_horizontal = ('produtos_fornecidos',)
    fieldsets = (
        ('Informações Básicas', {'fields': ('empresa', 'nome', 'mercado')}),
        ('Contato', {'fields': ('telefone', 'email', 'site')}),
        ('Endereço', {'fields': ('endereco',)}),
        ('Produtos', {'fields': ('produtos_fornecidos',)}),
        ('Descrição', {'fields': ('descricao',)}),
    )

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'mercado', 'data_cadastro')
    list_filter = ('mercado', 'data_cadastro')
    search_fields = ('nome', 'email', 'telefone')
    fieldsets = (
        ('Informações Básicas', {'fields': ('empresa', 'nome', 'mercado')}),
        ('Contato', {'fields': ('telefone', 'email', 'site')}),
        ('Endereço', {'fields': ('endereco',)}),
        ('Descrição', {'fields': ('descricao',)}),
    )

# --- Registro de Requisições de Compra ---
@admin.register(RequisicaoCompra)
class RequisicaoCompraAdmin(admin.ModelAdmin):
    list_display = ('item', 'requerente', 'status', 'valor_total_estimado', 'data_requisicao')
    list_filter = ('status', 'data_requisicao')
    search_fields = ('item', 'descricao', 'requerente__username', 'proposito')
    readonly_fields = ('data_requisicao', 'data_aprovacao', 'data_compra', 'data_recebimento')
    fieldsets = (
        ('Informações do Item', {'fields': ('item', 'descricao', 'quantidade', 'unidade', 'preco_estimado')}),
        ('Informações da Requisição', {'fields': ('proposito', 'projeto', 'requerente', 'status')}),
        ('Aprovação', {'fields': ('aprovado_por', 'data_aprovacao', 'observacao_aprovacao', 'documento_aprovacao')}),
        ('Compra', {'fields': ('comprado_por', 'data_compra', 'preco_real', 'fornecedor', 'nota_fiscal', 'data_entrega_prevista')}),
        ('Recebimento', {'fields': ('recebido_por', 'data_recebimento', 'observacao_recebimento')}),
    )


@admin.register(HistoricoRequisicao)
class HistoricoRequisicaoAdmin(admin.ModelAdmin):
    list_display = ('requisicao', 'tipo_alteracao', 'usuario', 'data_alteracao')
    list_filter = ('tipo_alteracao', 'data_alteracao')
    search_fields = ('requisicao__item', 'usuario__username', 'descricao')
    readonly_fields = ('requisicao', 'usuario', 'data_alteracao', 'tipo_alteracao', 'descricao')

    def has_add_permission(self, request):
        # Histórico é criado automaticamente, não permite adição manual
        return False

    def has_change_permission(self, request, obj=None):
        # Histórico não deve ser editado
        return False


# --- Registro de Gastos ---
@admin.register(GastoViagem)
class GastoViagemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'categoria', 'nota_fiscal', 'destino', 'data_viagem', 'enviado_financeiro', 'data_gasto')
    list_filter = ('data_gasto', 'data_viagem', 'categoria', 'enviado_financeiro')
    search_fields = ('descricao', 'destino', 'categoria', 'nota_fiscal', 'usuario__username')
    readonly_fields = ('data_gasto',)


@admin.register(GastoCaixaInterno)
class GastoCaixaInternoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'categoria', 'nota_fiscal', 'enviado_financeiro', 'data_gasto')
    list_filter = ('data_gasto', 'categoria', 'enviado_financeiro')
    search_fields = ('descricao', 'categoria', 'nota_fiscal', 'usuario__username')
    readonly_fields = ('data_gasto',)


# ==================================================
# ADMIN - SISTEMA DE PLANEJAMENTO DE PROJETOS
# ==================================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado_por', 'criado_em', 'ordem')
    list_editable = ('ordem',)
    list_filter = ('criado_em',)
    search_fields = ('nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        ('Informações Básicas', {'fields': ('nome', 'descricao', 'cor')}),
        ('Organização', {'fields': ('ordem', 'criado_por')}),
        ('Timestamps', {'fields': ('criado_em', 'atualizado_em')}),
    )


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('nome', 'project', 'status', 'data_inicio', 'data_fim', 'ordem')
    list_editable = ('ordem', 'status')
    list_filter = ('project', 'status', 'data_inicio')
    search_fields = ('nome', 'descricao')
    fieldsets = (
        ('Informações Básicas', {'fields': ('project', 'nome', 'descricao', 'cor')}),
        ('Datas', {'fields': ('data_inicio', 'data_fim')}),
        ('Status e Ordem', {'fields': ('status', 'ordem')}),
    )


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('nome', 'project', 'data_inicio', 'data_fim', 'ativo')
    list_filter = ('project', 'ativo', 'data_inicio')
    search_fields = ('nome', 'objetivo')
    fieldsets = (
        ('Informações Básicas', {'fields': ('project', 'nome', 'objetivo')}),
        ('Período', {'fields': ('data_inicio', 'data_fim')}),
        ('Status', {'fields': ('ativo',)}),
    )


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'project', 'cor')
    list_filter = ('project',)
    search_fields = ('nome', 'descricao')
    fieldsets = (
        ('Informações', {'fields': ('project', 'nome', 'descricao', 'cor')}),
    )


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'project', 'milestone', 'sprint', 'priority', 'status', 'data_inicio', 'data_fim', 'percentual_completo')
    list_filter = ('project', 'milestone', 'sprint', 'priority', 'status', 'finalizado')
    search_fields = ('titulo', 'descricao')
    filter_horizontal = ('responsaveis', 'labels')
    readonly_fields = ('criado_em', 'atualizado_em', 'quantidade_produzida', 'percentual_completo', 'dias_restantes', 'esta_atrasado')

    fieldsets = (
        ('Informações Básicas', {'fields': ('project', 'titulo', 'descricao')}),
        ('Organização', {'fields': ('milestone', 'sprint', 'parent_task', 'labels')}),
        ('Prioridade e Status', {'fields': ('priority', 'status', 'finalizado', 'data_finalizacao')}),
        ('Datas', {'fields': ('data_inicio', 'data_fim')}),
        ('Estimativa e Tracking', {'fields': ('estimativa', 'quantidade_meta', 'quantidade_produzida', 'percentual_completo')}),
        ('Responsáveis', {'fields': ('responsaveis', 'criado_por')}),
        ('Meta', {'fields': ('dias_restantes', 'esta_atrasado')}),
        ('Timestamps', {'fields': ('criado_em', 'atualizado_em', 'ordem')}),
    )

    def percentual_completo(self, obj):
        return f"{obj.percentual_completo}%"
    percentual_completo.short_description = 'Progresso'


@admin.register(ProjectAutomation)
class ProjectAutomationAdmin(admin.ModelAdmin):
    list_display = ('nome', 'project', 'trigger_type', 'action_type', 'ativo')
    list_filter = ('project', 'ativo', 'trigger_type', 'action_type')
    search_fields = ('nome',)
    fieldsets = (
        ('Informações Básicas', {'fields': ('project', 'nome', 'ativo')}),
        ('Gatilho (Trigger)', {'fields': ('trigger_type', 'trigger_value')}),
        ('Ação (Action)', {'fields': ('action_type', 'action_value')}),
    )

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'titulo', 'lida', 'criado_em')
    list_filter = ('tipo', 'lida', 'criado_em')
    search_fields = ('usuario__username', 'titulo', 'mensagem')
    readonly_fields = ('criado_em', 'lida_em')
    list_per_page = 50

