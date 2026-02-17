# core/models.py
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils import timezone

class Empresa(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Empresa")
    acesso_liberado = models.BooleanField(default=True, verbose_name="Acesso Liberado para Usuários")

    class Meta:
        verbose_name = "Empresa / Mercado"
        verbose_name_plural = "Empresas / Mercados"
    
    def __str__(self):
        return self.nome

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    empresas_permitidas = models.ManyToManyField(Empresa, blank=True)
    is_financeiro = models.BooleanField(default=False, verbose_name="É do Financeiro")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuário"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class Fornecedor(models.Model):
    MERCADO_CHOICES = [
        ('eletronico', 'Eletrônico'),
        ('metalurgica', 'Metalúrgica'),
        ('textil', 'Têxtil'),
        ('plastico', 'Plástico'),
        ('madeira', 'Madeira'),
        ('quimico', 'Químico'),
        ('alimenticio', 'Alimentício'),
        ('farmaceutico', 'Farmacêutico'),
        ('construcao', 'Construção'),
        ('automotivo', 'Automotivo'),
        ('tecnologia', 'Tecnologia'),
        ('servicos', 'Serviços'),
        ('outro', 'Outro'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    site = models.URLField(blank=True, null=True, verbose_name="Site")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    mercado = models.CharField(max_length=50, choices=MERCADO_CHOICES, blank=True, null=True, verbose_name="Mercado de Atuação")
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Data de Cadastro")

    # Mantendo compatibilidade
    link_site = models.URLField(blank=True, null=True, verbose_name="Website (deprecated)")

    class Meta:
        unique_together = ('empresa', 'nome')
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']

    def __str__(self): return self.nome

class Cliente(models.Model):
    MERCADO_CHOICES = [
        ('eletronico', 'Eletrônico'),
        ('metalurgica', 'Metalúrgica'),
        ('textil', 'Têxtil'),
        ('plastico', 'Plástico'),
        ('madeira', 'Madeira'),
        ('quimico', 'Químico'),
        ('alimenticio', 'Alimentício'),
        ('farmaceutico', 'Farmacêutico'),
        ('construcao', 'Construção'),
        ('automotivo', 'Automotivo'),
        ('tecnologia', 'Tecnologia'),
        ('servicos', 'Serviços'),
        ('outro', 'Outro'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200, verbose_name="Nome")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    site = models.URLField(blank=True, null=True, verbose_name="Site")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    mercado = models.CharField(max_length=50, choices=MERCADO_CHOICES, blank=True, null=True, verbose_name="Mercado de Atuação")
    produtos_fornecidos = models.ManyToManyField('ItemEstoque', blank=True, related_name='clientes', verbose_name="Produtos que Fornecemos")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    class Meta:
        unique_together = ('empresa', 'nome')
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']

    def __str__(self): return self.nome

class Setor(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, unique=True, help_text="Nome do setor")

    class Meta:
        unique_together = ('empresa', 'nome')

    def __str__(self): return self.nome

class ItemFornecedor(models.Model):
    item_estoque = models.ForeignKey('ItemEstoque', on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, null=True, blank=True)
    fornecedor_nome = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Fornecedor")
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor de Custo/Cotação")
    data_cotacao = models.DateField(verbose_name="Data da Cotação")

    def get_nome_fornecedor(self):
        """Retorna o nome do fornecedor, seja da FK ou do campo de texto"""
        if self.fornecedor:
            return self.fornecedor.nome
        return self.fornecedor_nome or "Fornecedor não informado"

    def __str__(self):
        return f"{self.item_estoque.nome} - {self.get_nome_fornecedor()}: R$ {self.valor_pago}"

class ItemEstoque(models.Model):
    TIPO_ITEM_CHOICES = [('componente', 'Componente / Matéria-Prima'), ('produto_acabado', 'Produto Acabado'),]
    tipo = models.CharField(max_length=20, choices=TIPO_ITEM_CHOICES, default='componente')
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Item")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    quantidade = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    local_armazenamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Local de Armazenamento")
    documentacao = models.FileField(upload_to='documentos_itens/', blank=True, null=True, verbose_name="Documentação")
    foto_principal = models.ImageField(upload_to='fotos_itens/', blank=True, null=True, verbose_name="Foto Principal")
    links = models.TextField(blank=True, null=True, verbose_name="Links", help_text="Links úteis (um por linha)")
    fornecedores = models.ManyToManyField(Fornecedor, through=ItemFornecedor, blank=True)
    is_produto_fabricado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def __str__(self): return f"{self.nome} ({self.quantidade} em estoque)"

class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    item = models.ForeignKey(ItemEstoque, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável")
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        ordering = ['-data_hora']
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"

    def __str__(self):
        return f"{self.tipo.upper()} - {self.item.nome} ({self.quantidade}) - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

class Recebimento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável")
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, verbose_name="Setor de Destino")
    foto_documento = models.ImageField(upload_to='fotos_documentos/', blank=True, null=True, verbose_name="Foto da Nota Fiscal/Documento")
    foto_embalagem = models.ImageField(upload_to='fotos_embalagens/', blank=True, null=True, verbose_name="Foto da Embalagem")
    data_recebimento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Recebimento")
    numero_nota_fiscal = models.CharField(max_length=100, verbose_name="Número da Nota Fiscal", blank=True, null=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fornecedor")
    fornecedor_nome = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Fornecedor")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor Total da Nota")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações Gerais")

    def get_nome_fornecedor(self):
        """Retorna o nome do fornecedor, seja da FK ou do campo de texto"""
        if self.fornecedor:
            return self.fornecedor.nome
        return self.fornecedor_nome or "Fornecedor não informado"

    STATUS_CHOICES = [('aguardando', 'Aguardando'), ('entregue', 'Entregue'),]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aguardando')
    
    def __str__(self): return f"Nota Fiscal {self.numero_nota_fiscal or 'N/A'}"

class ImagemItemEstoque(models.Model):
    item = models.ForeignKey(ItemEstoque, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='imagens_itens/')

    def __str__(self): return f"Imagem de {self.item.nome}"

class ProdutoFabricado(models.Model):
    item_associado = models.OneToOneField(ItemEstoque, on_delete=models.CASCADE, related_name='receita', null=True, blank=True)
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do Produto")
    foto_principal = models.ImageField(upload_to='fotos_produtos/', blank=True, null=True, verbose_name="Foto Principal")
    componentes = models.ManyToManyField(ItemEstoque, through='Componente', related_name='produtos_fabricados', verbose_name="Lista de Componentes")

    def __str__(self): return self.nome

class DocumentoProdutoFabricado(models.Model):
    produto = models.ForeignKey(ProdutoFabricado, related_name='documentos', on_delete=models.CASCADE)
    documento = models.FileField(upload_to='documentos_produtos/')
    TIPO_DOCUMENTO_CHOICES = [('manual', 'Manual de Instruções'), ('instalacao', 'Guia de Instalação'), ('manutencao', 'Guia de Manutenção'), ('garantia', 'Certificado de Garantia'), ('outro', 'Outro'),]
    tipo = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='outro')
    def __str__(self): return f"{self.get_tipo_display()} para {self.produto.nome}"

class ImagemProdutoFabricado(models.Model):
    produto = models.ForeignKey(ProdutoFabricado, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='imagens_produtos/')
    def __str__(self): return f"Imagem de {self.produto.nome}"

class Componente(models.Model):
    produto = models.ForeignKey(ProdutoFabricado, on_delete=models.CASCADE)
    item_estoque = models.ForeignKey(ItemEstoque, on_delete=models.PROTECT, verbose_name="Componente")
    quantidade_necessaria = models.PositiveIntegerField(verbose_name="Quantidade Necessária")
    
    def __str__(self): return f"{self.quantidade_necessaria}x {self.item_estoque.nome} para {self.produto.nome}"

class Expedicao(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    cliente = models.CharField(max_length=200, verbose_name="Cliente/Destino")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsável pela Expedição")
    data_expedicao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Expedição")
    nota_fiscal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número da Nota Fiscal")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def __str__(self):
        return f"Expedição #{self.pk} para {self.cliente}"

class ItemExpedido(models.Model):
    expedicao = models.ForeignKey(Expedicao, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(ProdutoFabricado, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} na Expedição #{self.expedicao.pk}"

class DocumentoExpedicao(models.Model):
    expedicao = models.ForeignKey(Expedicao, on_delete=models.CASCADE, related_name='documentos')
    documento = models.FileField(upload_to='documentos_expedicao/')
    TIPO_DOCUMENTO_CHOICES = [
        ('nota_fiscal', 'Nota Fiscal'),
        ('comprovante', 'Comprovante de Entrega'),
        ('ordem_envio', 'Ordem de Envio'),
        ('outro', 'Outro'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='outro')

    def __str__(self):
        return f"{self.get_tipo_display()} para a Expedição #{self.expedicao.pk}"

class ImagemExpedicao(models.Model):
    expedicao = models.ForeignKey(Expedicao, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='imagens_expedicao/')

    def __str__(self):
        return f"Imagem para a Expedição #{self.expedicao.pk}"


# ==================================================
# SISTEMA DE PLANEJAMENTO DE PROJETOS
# ==================================================

class Project(models.Model):
    """Projeto - agrupador principal de trabalho"""
    nome = models.CharField(max_length=200, verbose_name="Nome do Projeto")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    cor = models.CharField(max_length=20, default='#6366f1', verbose_name="Cor")  # Indigo
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='projetos_criados')
    ordem = models.PositiveIntegerField(default=0)
    membros = models.ManyToManyField(User, blank=True, related_name='projetos_participando', verbose_name="Membros")

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"

    def __str__(self):
        return self.nome


class Milestone(models.Model):
    """Marco importante do projeto - agrupa tarefas relacionadas"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    nome = models.CharField(max_length=200, verbose_name="Nome do Milestone")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Término")
    cor = models.CharField(max_length=20, default='#10b981', verbose_name="Cor")  # Green
    status = models.CharField(max_length=20, choices=[
        ('planejado', 'Planejado'),
        ('em_progresso', 'Em Progresso'),
        ('concluido', 'Concluído'),
        ('atrasado', 'Atrasado'),
    ], default='planejado', verbose_name="Status")
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'data_fim']
        verbose_name = "Milestone"
        verbose_name_plural = "Milestones"

    def __str__(self):
        return f"{self.nome} ({self.project.nome})"


class Sprint(models.Model):
    """Ciclo de trabalho (iteração) - para metodologia Agile"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    nome = models.CharField(max_length=200, verbose_name="Nome do Sprint")  # Ex: "Sprint 1", "Q1 2026"
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Término")
    objetivo = models.TextField(blank=True, verbose_name="Objetivo do Sprint")
    ativo = models.BooleanField(default=False, verbose_name="Sprint Ativo")  # Apenas 1 sprint ativo por projeto

    class Meta:
        ordering = ['-data_inicio']
        unique_together = ['project', 'nome']
        verbose_name = "Sprint"
        verbose_name_plural = "Sprints"

    def __str__(self):
        return f"{self.nome} ({self.project.nome})"


class Label(models.Model):
    """Sistema de tags/etiquetas para categorização de tarefas"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labels')
    nome = models.CharField(max_length=100, verbose_name="Nome da Label")
    cor = models.CharField(max_length=20, default='#6b7280', verbose_name="Cor")  # Gray
    descricao = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        ordering = ['nome']
        unique_together = ['project', 'nome']
        verbose_name = "Label"
        verbose_name_plural = "Labels"

    def __str__(self):
        return f"{self.nome} ({self.project.nome})"


class ProjectTask(models.Model):
    """Tarefa do projeto com campos customizados completos"""
    # Relações
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name="Projeto")
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name="Milestone")
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name="Sprint")
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks', verbose_name="Tarefa Pai")

    # Informações básicas
    titulo = models.CharField(max_length=300, verbose_name="Título")
    descricao = models.TextField(blank=True, verbose_name="Descrição")

    # Campos customizados
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ], default='medium', verbose_name="Prioridade")
    labels = models.ManyToManyField(Label, blank=True, related_name='tasks', verbose_name="Labels")

    # Datas
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Término")

    # Estimativa e tracking
    estimativa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                      help_text="Horas ou Story Points", verbose_name="Estimativa")
    quantidade_meta = models.PositiveIntegerField(default=0, help_text="Quantidade a produzir", verbose_name="Quantidade Meta")

    # Status
    status = models.CharField(max_length=20, choices=[
        ('todo', 'A Fazer'),
        ('in_progress', 'Em Progresso'),
        ('review', 'Em Revisão'),
        ('done', 'Concluído'),
        ('blocked', 'Bloqueado'),
    ], default='todo', verbose_name="Status")

    # Responsáveis
    responsaveis = models.ManyToManyField(User, blank=True, related_name='project_tasks', verbose_name="Responsáveis")

    # Flags
    finalizado = models.BooleanField(default=False, verbose_name="Finalizado")
    data_finalizacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Finalização")

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_criadas', verbose_name="Criado por")
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', '-criado_em']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['data_inicio', 'data_fim']),
        ]
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    @property
    def quantidade_produzida(self):
        """Total produzido somando todas as entradas"""
        total = self.quantidades_feitas.aggregate(total=Sum('quantidade'))['total']
        return total or 0

    @property
    def percentual_completo(self):
        """Percentual de conclusão baseado em quantidade"""
        if self.quantidade_meta == 0:
            return 100 if self.finalizado else 0
        return min(100, int((self.quantidade_produzida / self.quantidade_meta) * 100))

    @property
    def dias_restantes(self):
        """Dias até data_fim"""
        if not self.data_fim:
            return None
        delta = self.data_fim - timezone.now().date()
        return delta.days

    @property
    def esta_atrasado(self):
        """Verifica se está atrasado"""
        if not self.data_fim or self.finalizado:
            return False
        return timezone.now().date() > self.data_fim

    def __str__(self):
        return f"{self.titulo} ({self.project.nome})"


class TaskQuantidadeFeita(models.Model):
    """Registro de produção - tracking de quantidade produzida"""
    task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE, related_name='quantidades_feitas', verbose_name="Tarefa")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    data = models.DateTimeField(default=timezone.now, verbose_name="Data")
    observacoes = models.TextField(blank=True, verbose_name="Observações")

    class Meta:
        ordering = ['-data']
        verbose_name = "Quantidade Produzida"
        verbose_name_plural = "Quantidades Produzidas"

    def __str__(self):
        return f"{self.quantidade} unidades - {self.task.titulo}"


class TaskHistorico(models.Model):
    """Histórico completo de ações nas tarefas"""
    TIPO_ACAO_CHOICES = [
        ('criado', 'Criado'),
        ('editado', 'Editado'),
        ('movido', 'Movido para outro milestone'),
        ('iniciado', 'Iniciado'),
        ('finalizado', 'Finalizado'),
        ('reaberto', 'Reaberto'),
        ('bloqueado', 'Bloqueado'),
        ('desbloqueado', 'Desbloqueado'),
        ('quantidade_adicionada', 'Quantidade Adicionada'),
        ('responsavel_adicionado', 'Responsável Adicionado'),
        ('responsavel_removido', 'Responsável Removido'),
        ('label_adicionada', 'Label Adicionada'),
        ('label_removida', 'Label Removida'),
        ('prazo_alterado', 'Prazo Alterado'),
        ('priority_alterada', 'Prioridade Alterada'),
        ('subtask_criada', 'Subtarefa Criada'),
    ]
    task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE, related_name='historico', verbose_name="Tarefa")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    tipo_acao = models.CharField(max_length=30, choices=TIPO_ACAO_CHOICES, verbose_name="Tipo de Ação")
    descricao = models.TextField(verbose_name="Descrição")
    data = models.DateTimeField(default=timezone.now, verbose_name="Data")

    class Meta:
        ordering = ['-data']
        verbose_name = "Histórico de Tarefa"
        verbose_name_plural = "Histórico de Tarefas"

    def __str__(self):
        return f"{self.tipo_acao} - {self.task.titulo}"


class ProjectAutomation(models.Model):
    """Sistema de automações configuráveis"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='automations', verbose_name="Projeto")
    nome = models.CharField(max_length=200, verbose_name="Nome da Automação")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    # Trigger (gatilho)
    trigger_type = models.CharField(max_length=50, choices=[
        ('status_changed', 'Status Alterado'),
        ('task_created', 'Tarefa Criada'),
        ('task_assigned', 'Tarefa Atribuída'),
        ('due_date_approaching', 'Prazo Próximo'),
        ('task_overdue', 'Tarefa Atrasada'),
    ], verbose_name="Tipo de Gatilho")
    trigger_value = models.JSONField(null=True, blank=True, verbose_name="Configuração do Gatilho")

    # Action (ação)
    action_type = models.CharField(max_length=50, choices=[
        ('set_status', 'Definir Status'),
        ('assign_user', 'Atribuir Usuário'),
        ('add_label', 'Adicionar Label'),
        ('move_to_sprint', 'Mover para Sprint'),
        ('send_notification', 'Enviar Notificação'),
    ], verbose_name="Tipo de Ação")
    action_value = models.JSONField(null=True, blank=True, verbose_name="Configuração da Ação")

    class Meta:
        ordering = ['nome']
        verbose_name = "Automação"
        verbose_name_plural = "Automações"

    def __str__(self):
        return f"{self.nome} ({self.project.nome})"


# --- SISTEMA DE NOTIFICAÇÕES ---

class Notificacao(models.Model):
    """Notificações para usuários sobre tarefas e eventos"""
    TIPO_CHOICES = [
        ('tarefa_atribuida', 'Tarefa Atribuída'),
        ('tarefa_concluida', 'Tarefa Concluída'),
        ('prazo_proximo', 'Prazo Próximo'),
        ('tarefa_atrasada', 'Tarefa Atrasada'),
        ('comentario', 'Novo Comentário'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes', verbose_name="Usuário")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")

    # Link para a tarefa relacionada
    task = models.ForeignKey('ProjectTask', on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes', verbose_name="Tarefa")

    # Controle
    lida = models.BooleanField(default=False, verbose_name="Lida")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    lida_em = models.DateTimeField(null=True, blank=True, verbose_name="Lida em")

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario.username}"

    def marcar_como_lida(self):
        """Marca a notificação como lida"""
        if not self.lida:
            self.lida = True
            self.lida_em = timezone.now()
            self.save()


# --- MODELOS DE CONTROLE DE PONTO ---

class JornadaTrabalho(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jornada')
    horas_diarias = models.DecimalField(max_digits=4, decimal_places=2, default=9.0, verbose_name="Horas Diárias (padrão)")
    dias_semana = models.CharField(max_length=50, default="0,1,2,3,4", verbose_name="Dias da Semana",
                                   help_text="0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex, 5=Sáb, 6=Dom")
    horas_sexta = models.DecimalField(max_digits=4, decimal_places=2, default=8.0, verbose_name="Horas na Sexta")
    intervalo_almoco = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, verbose_name="Intervalo de Almoço (horas)")

    # Campos para período de mês customizado
    dia_inicio_mes = models.IntegerField(default=1, verbose_name="Dia de Início do Mês",
                                         help_text="Dia do mês em que inicia o período (1-31)")
    dia_fim_mes = models.IntegerField(default=0, verbose_name="Dia de Fim do Mês",
                                      help_text="Dia do mês em que termina o período (0=último dia do mês)")

    class Meta:
        verbose_name = "Jornada de Trabalho"
        verbose_name_plural = "Jornadas de Trabalho"

    def __str__(self):
        return f"{self.usuario.username} - {self.horas_diarias}h/dia"

    def horas_esperadas_dia(self, data):
        """Retorna horas esperadas para um dia específico"""
        # Segunda a Quinta (0-3): 9h líquidas (8-18 com 1h almoço)
        # Sexta (4): 8h líquidas (8-17 com 1h almoço)
        if data.weekday() == 4:  # Sexta
            return float(self.horas_sexta)
        else:  # Segunda a Quinta
            return float(self.horas_diarias)

    def horas_esperadas_periodo(self, data_inicio, data_fim):
        """Calcula horas esperadas para um período específico"""
        from datetime import timedelta
        total_horas = 0
        dias_trabalho = [int(d) for d in self.dias_semana.split(',')]

        dia_atual = data_inicio
        while dia_atual <= data_fim:
            if dia_atual.weekday() in dias_trabalho:
                total_horas += self.horas_esperadas_dia(dia_atual)
            dia_atual += timedelta(days=1)

        return total_horas

    @property
    def horas_mensais(self):
        """Calcula horas mensais baseado nos dias úteis e período personalizado"""
        import calendar
        from datetime import datetime
        now = datetime.now()

        # Se usa período padrão (dia 1 ao último dia do mês)
        if self.dia_inicio_mes == 1 and self.dia_fim_mes == 0:
            dias_no_mes = calendar.monthrange(now.year, now.month)[1]
            total_horas = 0
            dias_trabalho = [int(d) for d in self.dias_semana.split(',')]

            for dia in range(1, dias_no_mes + 1):
                data = datetime(now.year, now.month, dia)
                if data.weekday() in dias_trabalho:
                    total_horas += self.horas_esperadas_dia(data)

            return total_horas
        else:
            # Usa período personalizado - calcula com base no dia atual
            dia_inicio = self.dia_inicio_mes
            dia_fim = self.dia_fim_mes if self.dia_fim_mes != 0 else calendar.monthrange(now.year, now.month)[1]

            # Determinar primeiro e último dia do período atual
            if now.day >= dia_inicio:
                # Período atual
                primeiro_dia = datetime(now.year, now.month, dia_inicio).date()

                if dia_fim >= dia_inicio:
                    # Termina no mesmo mês
                    ultimo_dia = datetime(now.year, now.month, dia_fim).date()
                else:
                    # Termina no próximo mês
                    if now.month == 12:
                        proximo_mes = 1
                        proximo_ano = now.year + 1
                    else:
                        proximo_mes = now.month + 1
                        proximo_ano = now.year
                    ultimo_dia = datetime(proximo_ano, proximo_mes, dia_fim).date()
            else:
                # Período anterior
                if now.month == 1:
                    mes_anterior = 12
                    ano_anterior = now.year - 1
                else:
                    mes_anterior = now.month - 1
                    ano_anterior = now.year

                primeiro_dia = datetime(ano_anterior, mes_anterior, dia_inicio).date()
                ultimo_dia = datetime(now.year, now.month, dia_fim).date()

            return self.horas_esperadas_periodo(primeiro_dia, ultimo_dia)

class RegistroPonto(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('inicio_almoco', 'Início Almoço'),
        ('fim_almoco', 'Fim Almoço'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pontos')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    data_hora = models.DateTimeField(default=timezone.now)
    localizacao = models.CharField(max_length=200, blank=True, null=True, verbose_name="Localização")
    observacao = models.TextField(blank=True, null=True)

    # Campos de Abono
    abonado = models.BooleanField(default=False, verbose_name="Abonado")
    motivo_abono = models.TextField(blank=True, null=True, verbose_name="Motivo do Abono")
    abonado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='abonos_concedidos', verbose_name="Abonado por")
    data_abono = models.DateTimeField(null=True, blank=True, verbose_name="Data do Abono")

    class Meta:
        ordering = ['-data_hora']
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

class AbonoDia(models.Model):
    TIPO_ABONO_CHOICES = [
        ('doenca', 'Doença'),
        ('atestado', 'Atestado Médico'),
        ('falta_justificada', 'Falta Justificada'),
        ('licenca', 'Licença'),
        ('ferias', 'Férias'),
        ('outro', 'Outro'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abonos_dias')
    data = models.DateField(verbose_name="Data do Abono")
    tipo_abono = models.CharField(max_length=20, choices=TIPO_ABONO_CHOICES, verbose_name="Tipo de Abono")
    motivo = models.TextField(verbose_name="Motivo/Justificativa")
    abonado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='abonos_dias_concedidos', verbose_name="Abonado por")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    horas_abonadas = models.DecimalField(max_digits=4, decimal_places=2, default=8.0, verbose_name="Horas Abonadas")

    class Meta:
        ordering = ['-data']
        verbose_name = "Abono de Dia"
        verbose_name_plural = "Abonos de Dias"
        unique_together = ['usuario', 'data']

    def __str__(self):
        return f"{self.usuario.username} - {self.data.strftime('%d/%m/%Y')} - {self.get_tipo_abono_display()}"

class ResumoMensal(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumos_mensais')
    mes = models.IntegerField()
    ano = models.IntegerField()
    horas_trabalhadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    horas_esperadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    saldo_horas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    dias_presentes = models.IntegerField(default=0)
    dias_ausentes = models.IntegerField(default=0)

    class Meta:
        ordering = ['-ano', '-mes']
        unique_together = ['usuario', 'mes', 'ano']
        verbose_name = "Resumo Mensal"
        verbose_name_plural = "Resumos Mensais"

    def __str__(self):
        return f"{self.usuario.username} - {self.mes}/{self.ano}"


class RequisicaoCompra(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Aguardando Aprovação'),
        ('aprovado', 'Aprovado - Aguardando Compra'),
        ('comprado', 'Comprado - Aguardando Recebimento'),
        ('recebido', 'Pedido Concluído'),
        ('rejeitado', 'Rejeitado'),
    ]

    # Informações básicas
    item = models.CharField(max_length=200, verbose_name="Item")
    descricao = models.TextField(verbose_name="Descrição")
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantidade")
    unidade = models.CharField(max_length=20, default="un", verbose_name="Unidade")
    preco_estimado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Estimado (R$)")

    # Informações da requisição
    proposito = models.CharField(max_length=200, verbose_name="Propósito")
    produto = models.ForeignKey('ProdutoFabricado', on_delete=models.SET_NULL, blank=True, null=True, related_name='requisicoes', verbose_name="Produto")
    link_item = models.URLField(blank=True, null=True, verbose_name="Link do Item")
    requerente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisicoes', verbose_name="Requerente")

    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    data_requisicao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Requisição")

    # Aprovação
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprovacoes_compra', verbose_name="Aprovado Por")
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    observacao_aprovacao = models.TextField(blank=True, null=True, verbose_name="Observação da Aprovação")
    documento_aprovacao = models.FileField(upload_to='requisicoes/aprovacao/', blank=True, null=True, verbose_name="Documento/Imagem de Aprovação")

    # Compra
    comprado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras_realizadas', verbose_name="Comprado Por")
    data_compra = models.DateTimeField(null=True, blank=True, verbose_name="Data da Compra")
    preco_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço Real (R$)")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fornecedor")
    fornecedor_nome_digitado = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Fornecedor (digitado)")
    nota_fiscal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nota Fiscal")
    data_entrega_prevista = models.DateField(null=True, blank=True, verbose_name="Data de Entrega Prevista")

    # Dados de pagamento
    FORMA_PAGAMENTO_CHOICES = [
        ('pix', 'PIX'),
        ('dinheiro', 'Dinheiro'),
        ('transferencia_bancaria', 'Transferência Bancária'),
        ('boleto', 'Boleto'),
        ('cartao', 'Cartão'),
    ]
    forma_pagamento = models.CharField(max_length=30, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True, verbose_name="Forma de Pagamento")

    # Campos específicos para boleto
    quantidade_parcelas = models.IntegerField(blank=True, null=True, verbose_name="Quantidade de Parcelas")

    # Tipo de dias de pagamento
    TIPO_DIAS_CHOICES = [
        ('15_em_15', 'De 15 em 15 dias'),
        ('30_em_30', 'De 30 em 30 dias'),
        ('especificos', 'Dias específicos'),
    ]
    tipo_dias_pagamento = models.CharField(max_length=20, choices=TIPO_DIAS_CHOICES, blank=True, null=True, verbose_name="Tipo de Dias de Pagamento")
    dias_pagamento = models.TextField(blank=True, null=True, verbose_name="Dias de Pagamento", help_text="Exemplo: '15, 30, 45' ou '29 de fevereiro'")

    documento_boleto = models.FileField(upload_to='requisicoes/boletos/', blank=True, null=True, verbose_name="Documento do Boleto")
    dias_aviso_pagamento = models.IntegerField(blank=True, null=True, default=3, verbose_name="Dias de Antecedência para Aviso", help_text="Quantos dias antes do vencimento enviar alerta")

    # Documento da nota fiscal
    documento_nota_fiscal = models.FileField(upload_to='requisicoes/notas_fiscais/', blank=True, null=True, verbose_name="Documento da Nota Fiscal")

    # Recebimento
    recebido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='recebimentos_compra', verbose_name="Recebido Por")
    data_recebimento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Recebimento")
    observacao_recebimento = models.TextField(blank=True, null=True, verbose_name="Observação do Recebimento")

    class Meta:
        ordering = ['-data_requisicao']
        verbose_name = "Requisição de Compra"
        verbose_name_plural = "Requisições de Compra"

    def __str__(self):
        return f"{self.item} - {self.get_status_display()}"

    def valor_total_estimado(self):
        return self.quantidade * self.preco_estimado

    def valor_total_real(self):
        if self.preco_real:
            return self.quantidade * self.preco_real
        return None


class HistoricoRequisicao(models.Model):
    """Histórico de alterações em requisições de compra"""
    requisicao = models.ForeignKey(RequisicaoCompra, on_delete=models.CASCADE, related_name='historico', verbose_name="Requisição")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário")
    data_alteracao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Alteração")
    tipo_alteracao = models.CharField(max_length=100, verbose_name="Tipo de Alteração")
    descricao = models.TextField(verbose_name="Descrição das Alterações")

    class Meta:
        ordering = ['-data_alteracao']
        verbose_name = "Histórico de Requisição"
        verbose_name_plural = "Históricos de Requisições"

    def __str__(self):
        return f"{self.requisicao.item} - {self.tipo_alteracao} por {self.usuario} em {self.data_alteracao.strftime('%d/%m/%Y %H:%M')}"


class ParcelaBoleto(models.Model):
    """Controle de parcelas individuais de boletos"""
    requisicao = models.ForeignKey(
        RequisicaoCompra,
        on_delete=models.CASCADE,
        related_name='parcelas_boleto',
        verbose_name="Requisição"
    )
    numero_parcela = models.IntegerField(verbose_name="Número da Parcela")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor da Parcela"
    )

    # Controle de pagamento
    pago = models.BooleanField(default=False, verbose_name="Pago")
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do Pagamento"
    )
    comprovante = models.FileField(
        upload_to='comprovantes_boleto/',
        null=True,
        blank=True,
        verbose_name="Comprovante"
    )
    pago_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boletos_pagos',
        verbose_name="Pago por"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['data_vencimento', 'numero_parcela']
        verbose_name = "Parcela de Boleto"
        verbose_name_plural = "Parcelas de Boleto"
        unique_together = ['requisicao', 'numero_parcela']

    def __str__(self):
        status = "✅ Pago" if self.pago else "⏳ Pendente"
        return f"Parcela {self.numero_parcela} - {self.requisicao.item} - {status}"


# ==================================================
# MODELOS DE GASTOS
# ==================================================

class GastoViagem(models.Model):
    """Gastos realizados em viagens"""
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    descricao = models.TextField(verbose_name="Descrição")
    imagem = models.ImageField(upload_to='gastos_viagem/', blank=True, null=True, verbose_name="Comprovante/Foto")
    data_gasto = models.DateTimeField(auto_now_add=True, verbose_name="Data do Gasto")
    data_viagem = models.DateField(null=True, blank=True, verbose_name="Data da Viagem")
    destino = models.CharField(max_length=200, blank=True, null=True, verbose_name="Destino")
    categoria = models.CharField(max_length=100, blank=True, null=True, verbose_name="Categoria")
    nota_fiscal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número da Nota Fiscal")
    enviado_financeiro = models.BooleanField(default=False, verbose_name="Enviado ao Financeiro")

    class Meta:
        ordering = ['-data_gasto']
        verbose_name = "Gasto de Viagem"
        verbose_name_plural = "Gastos de Viagem"

    def __str__(self):
        return f"{self.usuario} - R$ {self.valor} - {self.data_gasto.strftime('%d/%m/%Y')}"


class GastoCaixaInterno(models.Model):
    """Gastos do caixa interno da empresa"""
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    descricao = models.TextField(verbose_name="Descrição")
    imagem = models.ImageField(upload_to='gastos_caixa/', blank=True, null=True, verbose_name="Comprovante/Foto")
    data_gasto = models.DateTimeField(auto_now_add=True, verbose_name="Data do Gasto")
    categoria = models.CharField(max_length=100, blank=True, null=True, verbose_name="Categoria")
    nota_fiscal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número da Nota Fiscal")
    enviado_financeiro = models.BooleanField(default=False, verbose_name="Enviado ao Financeiro")

    class Meta:
        ordering = ['-data_gasto']
        verbose_name = "Gasto de Caixa Interno"
        verbose_name_plural = "Gastos de Caixa Interno"

    def __str__(self):
        return f"{self.usuario} - R$ {self.valor} - {self.data_gasto.strftime('%d/%m/%Y')}"
