from django import forms
from .models import (
    ItemEstoque, Recebimento, ProdutoFabricado, 
    DocumentoProdutoFabricado, Componente, ImagemProdutoFabricado,
    Fornecedor, ItemFornecedor
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
            'documentacao': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 ...'}),
            'foto_principal': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 ...'}),
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
        fields = ['numero_nota_fiscal', 'fornecedor', 'valor_total', 'data_cotacao', 'setor', 'foto_documento', 'foto_embalagem', 'observacoes']
        widgets = {
            'numero_nota_fiscal': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'fornecedor': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'valor_total': forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'data_cotacao': forms.DateInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...', 'type': 'date' }),
            'setor': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'observacoes': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...', 'rows': 3}),
        }

# --- Formulários de Produto ---

class ProdutoFabricadoForm(forms.ModelForm):
    class Meta:
        model = ProdutoFabricado
        fields = ['nome', 'descricao', 'foto_principal']
        # ADICIONADO: Widgets para estilizar os campos
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 4
            }),
            'foto_principal': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
        }
class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = ['item_estoque', 'quantidade_necessaria']
        labels = {
            'item_estoque': 'Componente',
            'quantidade_necessaria': 'Qtd. Necessária',
        }
        widgets = {
            'item_estoque': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            # A LINHA QUE ESTAVA FALTANDO
            'quantidade_necessaria': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
        }
class DocumentoProdutoForm(forms.ModelForm):
    class Meta:
        model = DocumentoProdutoFabricado
        fields = ['documento', 'tipo']
        labels = {
            'documento': 'Arquivo',
            'tipo': 'Tipo de Documento',
        }
        # ADICIONADO: Widgets para estilizar os campos do formset
        widgets = {
            'documento': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
            'tipo': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
        }
# O FORMULÁRIO QUE ESTAVA FALTANDO
class ImagemProdutoForm(forms.ModelForm):
    class Meta:
        model = ImagemProdutoFabricado
        fields = ['imagem']

class ProducaoForm(forms.Form):
    quantidade_a_produzir = forms.IntegerField(min_value=1, label="Quantidade a Produzir", initial=1, widget=forms.NumberInput(attrs={'class': '...'}))

class ItemFornecedorForm(forms.ModelForm):
    class Meta:
        model = ItemFornecedor
        fields = ['fornecedor', 'valor_pago', 'data_cotacao']
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'tom-select'}),
            'data_cotacao': forms.DateInput(attrs={'type': 'date'})
            }