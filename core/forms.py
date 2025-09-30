from django import forms
from .models import (
    ItemEstoque, Recebimento, ProdutoFabricado, 
    DocumentoProdutoFabricado, Componente, ImagemProdutoFabricado,
    Fornecedor, ItemFornecedor, Expedicao, ItemExpedido, DocumentoExpedicao, ImagemExpedicao
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

class AdicaoItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade a ser Adicionada",
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm',
            'placeholder': 'Ex: 25'
        })
    )

    
# Formulário para registrar um novo RECEBIMENTO
class RecebimentoForm(forms.ModelForm):
    class Meta:
        model = Recebimento
        # O campo 'empresa' DEVE estar na lista para que a view possa acessá-lo
        fields = ['empresa', 'numero_nota_fiscal', 'fornecedor', 'valor_total', 'setor', 'status', 'foto_documento', 'foto_embalagem', 'observacoes']
        labels = {
            'empresa': 'Registrar para a Empresa',
            'numero_nota_fiscal': 'Número da Nota Fiscal',
            'fornecedor': 'Fornecedor',
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
            'fornecedor': forms.Select(attrs={'class': 'tom-select-criavel mt-1 block w-full ...'}),
            'valor_total': forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'setor': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...'}),
            'observacoes': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md ...', 'rows': 3}),
            'foto_documento': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 ...'}),
            'foto_embalagem': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 ...'}),
        }

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
        fields = ['fornecedor', 'valor_pago', 'data_cotacao']
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'tom-select'}),
            'data_cotacao': forms.DateInput(attrs={'type': 'date'})
            }

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