# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Empresa")
    # Este é o "interruptor" que o superusuário poderá usar
    acesso_liberado = models.BooleanField(default=True, verbose_name="Acesso Liberado para Usuários")
    
    def __str__(self):
        return self.nome

class PerfilUsuario(models.Model):
    # OneToOneField cria um link direto e único com o modelo de usuário do Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    # ManyToManyField permite que um usuário tenha acesso a várias empresas
    empresas_permitidas = models.ManyToManyField(Empresa, blank=True)

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


class SaidaProduto(models.Model):
    produto = models.ForeignKey(ProdutoFabricado, on_delete=models.PROTECT, verbose_name="Produto Enviado")
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade Enviada")
    cliente = models.CharField(max_length=200, verbose_name="Cliente")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável pela Saída")
    nota_fiscal = models.FileField(upload_to='notas_fiscais/', blank=True, null=True, verbose_name="Nota Fiscal")
    foto_saida = models.ImageField(upload_to='fotos_saidas/', blank=True, null=True, verbose_name="Foto da Saída")
    data_saida = models.DateTimeField(auto_now_add=True, verbose_name="Data da Saída")
    def __str__(self): return f"Saída de {self.quantidade}x {self.produto.nome} para {self.cliente}"

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
