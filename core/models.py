# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text="Nome do setor")
    def __str__(self): return self.nome

class ItemEstoque(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Item")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    quantidade = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    local_armazenamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Local de Armazenamento")
    documentacao = models.FileField(upload_to='documentos_itens/', blank=True, null=True, verbose_name="Documentação")
    # O CAMPO QUE ESTAVA FALTANDO
    foto_principal = models.ImageField(upload_to='fotos_itens/', blank=True, null=True, verbose_name="Foto Principal")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    def __str__(self): return f"{self.nome} ({self.quantidade} em estoque)"

class ImagemItemEstoque(models.Model):
    item = models.ForeignKey(ItemEstoque, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='imagens_itens/')
    def __str__(self): return f"Imagem de {self.item.nome}"

class ProdutoFabricado(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Produto")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do Produto")
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

class Recebimento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável")
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, verbose_name="Setor de Destino")
    foto_documento = models.ImageField(upload_to='fotos_documentos/', blank=True, null=True, verbose_name="Foto da Nota Fiscal/Documento")
    foto_embalagem = models.ImageField(upload_to='fotos_embalagens/', blank=True, null=True, verbose_name="Foto da Embalagem")
    data_recebimento = models.DateTimeField(auto_now_add=True, verbose_name="Data do Recebimento")
    descricao_pacote = models.TextField(verbose_name="Descrição do Pacote")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações Gerais")
    STATUS_CHOICES = [('aguardando', 'Aguardando Armazenamento'), ('armazenado', 'Armazenado'), ('concluido', 'Concluído'),]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aguardando')
    def __str__(self): return f"Pacote recebido por {self.usuario.username or 'desconhecido'} em {self.data_recebimento.strftime('%d/%m/%Y')}"

class SaidaProduto(models.Model):
    produto = models.ForeignKey(ProdutoFabricado, on_delete=models.PROTECT, verbose_name="Produto Enviado")
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade Enviada")
    cliente = models.CharField(max_length=200, verbose_name="Cliente")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável pela Saída")
    nota_fiscal = models.FileField(upload_to='notas_fiscais/', blank=True, null=True, verbose_name="Nota Fiscal")
    foto_saida = models.ImageField(upload_to='fotos_saidas/', blank=True, null=True, verbose_name="Foto da Saída")
    data_saida = models.DateTimeField(auto_now_add=True, verbose_name="Data da Saída")
    def __str__(self): return f"Saída de {self.quantidade}x {self.produto.nome} para {self.cliente}"