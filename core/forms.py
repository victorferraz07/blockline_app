from django import forms
from .models import (
    ItemEstoque, Recebimento, ProdutoFabricado,
    DocumentoProdutoFabricado, Componente, ImagemProdutoFabricado,
    Fornecedor, ItemFornecedor, Expedicao, ItemExpedido, DocumentoExpedicao, ImagemExpedicao,
    Cliente
)

# Formulário para CRIAR e EDITAR um Item de Estoque
class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ['nome', 'descricao', 'quantidade', 'local_armazenamento', 'documentacao', 'foto_principal']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'descricao': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...', 'rows': 4}),
            'quantidade': forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'local_armazenamento': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'documentacao': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'foto_principal': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

# Formulário para a AÇÃO de RETIRADA
class RetiradaItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade a ser Retirada",
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Ex: 10'
        })
    )
    observacoes = forms.CharField(
        required=False,
        label="Observações (opcional)",
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Descreva o motivo da retirada...',
            'rows': 3
        })
    )

class AdicaoItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade a ser Adicionada",
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Ex: 25'
        })
    )
    observacoes = forms.CharField(
        required=False,
        label="Observações (opcional)",
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Descreva o motivo da adição...',
            'rows': 3
        })
    )

    
# Formulário para registrar um novo RECEBIMENTO
class RecebimentoForm(forms.ModelForm):
    class Meta:
        model = Recebimento
        # O campo 'empresa' DEVE estar na lista para que a view possa acessá-lo
        fields = ['empresa', 'numero_nota_fiscal', 'fornecedor', 'fornecedor_nome', 'valor_total', 'setor', 'status', 'foto_documento', 'foto_embalagem', 'observacoes']
        labels = {
            'empresa': 'Registrar para a Empresa',
            'numero_nota_fiscal': 'Número da Nota Fiscal',
            'fornecedor': 'Fornecedor Cadastrado (opcional)',
            'fornecedor_nome': 'Ou digite o nome do fornecedor',
            'valor_total': 'Valor Total da Nota',
            'setor': 'Setor de Destino',
            'status': 'Status',
            'foto_documento': 'Foto da Nota Fiscal/Documento',
            'foto_embalagem': 'Foto da Embalagem',
            'observacoes': 'Observações Gerais',
        }
        widgets = {
            'empresa': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'numero_nota_fiscal': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'fornecedor': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm'}),
            'fornecedor_nome': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm', 'placeholder': 'Digite o nome do fornecedor'}),
            'valor_total': forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'setor': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'observacoes': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...', 'rows': 3}),
            'foto_documento': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 ...'}),
            'foto_embalagem': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 ...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fornecedor = cleaned_data.get('fornecedor')
        fornecedor_nome = cleaned_data.get('fornecedor_nome')

        if not fornecedor and not fornecedor_nome:
            raise forms.ValidationError('Selecione um fornecedor cadastrado ou digite o nome.')

        return cleaned_data

# --- Formulários de Produto ---

class ProdutoFabricadoForm(forms.ModelForm):
    class Meta:
        model = ProdutoFabricado
        fields = ['nome', 'descricao', 'foto_principal']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'descricao': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 4}),
            'foto_principal': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }
class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = ['item_estoque', 'quantidade_necessaria']
        labels = {'item_estoque': '', 'quantidade_necessaria': ''}
        widgets = {
            'item_estoque': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'quantidade_necessaria': forms.NumberInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
class DocumentoProdutoForm(forms.ModelForm):
    class Meta:
        model = DocumentoProdutoFabricado
        fields = ['documento', 'tipo']
        labels = {'documento': 'Arquivo', 'tipo': 'Tipo de Documento'}
        widgets = {
            'documento': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'tipo': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
# O FORMULÁRIO QUE ESTAVA FALTANDO
class ImagemProdutoForm(forms.ModelForm):
    class Meta:
        model = ImagemProdutoFabricado
        fields = ['imagem']
        labels = {'imagem': ''}
        widgets = {
            'imagem': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

class ProducaoForm(forms.Form):
    quantidade_a_produzir = forms.IntegerField(
        min_value=1,
        label="Quantidade a Produzir",
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-xl  md:font-bold'
        })
    )

class ItemFornecedorForm(forms.ModelForm):
    class Meta:
        model = ItemFornecedor
        fields = ['fornecedor', 'fornecedor_nome', 'valor_pago', 'data_cotacao']
        labels = {
            'fornecedor': 'Fornecedor Cadastrado (opcional)',
            'fornecedor_nome': 'Ou digite o nome do fornecedor',
            'valor_pago': 'Valor (R$)',
            'data_cotacao': 'Data da Cotação',
        }
        widgets = {
            'fornecedor': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'fornecedor_nome': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': 'Digite o nome do fornecedor se não estiver cadastrado'
            }),
            'valor_pago': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'data_cotacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        fornecedor = cleaned_data.get('fornecedor')
        fornecedor_nome = cleaned_data.get('fornecedor_nome')

        if not fornecedor and not fornecedor_nome:
            raise forms.ValidationError('Selecione um fornecedor cadastrado ou digite o nome.')

        return cleaned_data

class ExpedicaoForm(forms.ModelForm):
    class Meta:
        model = Expedicao
        fields = fields = ['empresa', 'cliente', 'nota_fiscal', 'observacoes']
        labels = {
            'cliente': 'Cliente / Destino',
            'nota_fiscal': 'Número da Nota Fiscal',
            'observacoes': 'Observações Gerais',
        }
        widgets = {
            'cliente': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'nota_fiscal': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'observacoes': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 3}),
        }

class ItemExpedidoForm(forms.ModelForm):
    class Meta:
        model = ItemExpedido
        fields = ['produto', 'quantidade']
        labels = {'produto': '', 'quantidade': ''}
        widgets = {
            'produto': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'quantidade': forms.NumberInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }

class DocumentoExpedicaoForm(forms.ModelForm):
    class Meta:
        model = DocumentoExpedicao
        fields = ['documento', 'tipo']
        labels = {'documento': '', 'tipo': ''}
        widgets = {
            'documento': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'tipo': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }

class ImagemExpedicaoForm(forms.ModelForm):
    class Meta:
        model = ImagemExpedicao
        fields = ['imagem']
        labels = {'imagem': ''}
        widgets = {
            'imagem': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

# Formulários para Fornecedor e Cliente
class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'endereco', 'telefone', 'email', 'site', 'mercado', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'}),
            'endereco': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'rows': 3}),
            'telefone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'placeholder': '(00) 0000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'placeholder': 'exemplo@email.com'}),
            'site': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'placeholder': 'https://exemplo.com'}),
            'mercado': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'}),
            'descricao': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'rows': 4}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'endereco', 'telefone', 'email', 'site', 'mercado', 'descricao', 'produtos_fornecidos']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'}),
            'endereco': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'rows': 3}),
            'telefone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'placeholder': '(00) 0000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'placeholder': 'exemplo@email.com'}),
            'site': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'placeholder': 'https://exemplo.com'}),
            'mercado': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent'}),
            'descricao': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'rows': 4}),
            'produtos_fornecidos': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'size': '6'}),
        }