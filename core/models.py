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
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    empresas_permitidas = models.ManyToManyField(Empresa, blank=True)
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuário"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class Fornecedor(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    link_site = models.URLField(blank=True, null=True, verbose_name="Website")

    class Meta:
        unique_together = ('empresa', 'nome')

    def __str__(self): return self.nome

class Setor(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, unique=True, help_text="Nome do setor")

    class Meta:
        unique_together = ('empresa', 'nome')

    def __str__(self): return self.nome

class ItemFornecedor(models.Model):
    item_estoque = models.ForeignKey('ItemEstoque', on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor de Custo/Cotação")
    data_cotacao = models.DateField(verbose_name="Data da Cotação")
    def __str__(self): return f"{self.item_estoque.nome} - {self.fornecedor.nome}: R$ {self.valor_pago}"

class ItemEstoque(models.Model):
    TIPO_ITEM_CHOICES = [('componente', 'Componente / Matéria-Prima'), ('produto_acabado', 'Produto Acabado'),]
    tipo = models.CharField(max_length=20, choices=TIPO_ITEM_CHOICES, default='componente')
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Item")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    quantidade = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    local_armazenamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Local de Armazenamento")
    documentacao = models.FileField(upload_to='documentos_itens/', blank=True, null=True, verbose_name="Documentação")
    foto_principal = models.ImageField(upload_to='fotos_itens/', blank=True, null=True, verbose_name="Foto Principal")
    fornecedores = models.ManyToManyField(Fornecedor, through=ItemFornecedor, blank=True)
    is_produto_fabricado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def __str__(self): return f"{self.nome} ({self.quantidade} em estoque)"

class Recebimento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável")
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, verbose_name="Setor de Destino")
    foto_documento = models.ImageField(upload_to='fotos_documentos/', blank=True, null=True, verbose_name="Foto da Nota Fiscal/Documento")
    foto_embalagem = models.ImageField(upload_to='fotos_embalagens/', blank=True, null=True, verbose_name="Foto da Embalagem")
    data_recebimento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Recebimento")
    numero_nota_fiscal = models.CharField(max_length=100, verbose_name="Número da Nota Fiscal", blank=True, null=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fornecedor")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor Total da Nota")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações Gerais")

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

# --- MODELOS KANBAN ---

class KanbanColumn(models.Model):
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=20, default='#f3f4f6')  # cor de fundo
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']
    def __str__(self):
        return self.nome

class Task(models.Model):
    coluna = models.ForeignKey(KanbanColumn, on_delete=models.CASCADE, related_name='tasks')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    quantidade_meta = models.PositiveIntegerField(default=0, verbose_name="Quantidade Meta")
    em_andamento = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    responsaveis = models.ManyToManyField(User, blank=True, related_name='tasks_responsaveis')
    ordem = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.titulo

    @property
    def quantidade_produzida(self):
        """Soma total de quantidade produzida por todos os usuários"""
        return self.quantidades_feitas.aggregate(total=Sum('quantidade'))['total'] or 0

    @property
    def quantidade_restante(self):
        """Quantidade que ainda falta produzir"""
        return max(0, self.quantidade_meta - self.quantidade_produzida)

    @property
    def percentual_completo(self):
        """Percentual de conclusão da tarefa"""
        if self.quantidade_meta == 0:
            return 0
        return min(100, int((self.quantidade_produzida / self.quantidade_meta) * 100))

class TaskQuantidadeFeita(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='quantidades_feitas')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-data']
    def __str__(self):
        return f"{self.quantidade} feita por {self.usuario} em {self.data.strftime('%d/%m/%Y %H:%M')}"

class TaskHistorico(models.Model):
    TIPO_ACAO_CHOICES = [
        ('criado', 'Criado'),
        ('movido', 'Movido'),
        ('editado', 'Editado'),
        ('iniciado', 'Iniciado'),
        ('finalizado', 'Finalizado'),
        ('quantidade_adicionada', 'Quantidade Adicionada'),
        ('responsavel_adicionado', 'Responsável Adicionado'),
        ('responsavel_removido', 'Responsável Removido'),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_acao = models.CharField(max_length=30, choices=TIPO_ACAO_CHOICES)
    descricao = models.TextField()
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-data']
        verbose_name = "Histórico da Tarefa"
        verbose_name_plural = "Históricos das Tarefas"

    def __str__(self):
        return f"{self.get_tipo_acao_display()} - {self.task.titulo} ({self.data.strftime('%d/%m/%Y %H:%M')})"

# --- MODELOS DE CONTROLE DE PONTO ---

class JornadaTrabalho(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jornada')
    horas_diarias = models.DecimalField(max_digits=4, decimal_places=2, default=8.0, verbose_name="Horas Diárias")
    dias_semana = models.CharField(max_length=50, default="1,2,3,4,5", verbose_name="Dias da Semana",
                                   help_text="0=Dom, 1=Seg, 2=Ter, 3=Qua, 4=Qui, 5=Sex, 6=Sáb")

    class Meta:
        verbose_name = "Jornada de Trabalho"
        verbose_name_plural = "Jornadas de Trabalho"

    def __str__(self):
        return f"{self.usuario.username} - {self.horas_diarias}h/dia"

    @property
    def horas_mensais(self):
        """Calcula horas mensais baseado nos dias úteis"""
        import calendar
        from datetime import datetime
        now = datetime.now()
        dias_no_mes = calendar.monthrange(now.year, now.month)[1]
        dias_uteis = 0
        dias_trabalho = [int(d) for d in self.dias_semana.split(',')]

        for dia in range(1, dias_no_mes + 1):
            data = datetime(now.year, now.month, dia)
            if data.weekday() in dias_trabalho:
                dias_uteis += 1

        return float(self.horas_diarias) * dias_uteis

class RegistroPonto(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pontos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    data_hora = models.DateTimeField(default=timezone.now)
    localizacao = models.CharField(max_length=200, blank=True, null=True, verbose_name="Localização")
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data_hora']
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

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
