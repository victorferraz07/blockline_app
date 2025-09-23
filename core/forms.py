# core/forms.py
from django import forms
from .models import ItemEstoque, Recebimento, ProdutoFabricado, DocumentoProdutoFabricado, Componente, ImagemProdutoFabricado

class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ['nome', 'descricao', 'quantidade', 'local_armazenamento', 'documentacao', 'foto_principal']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'descricao': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 4}),
            'quantidade': forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'local_armazenamento': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'documentacao': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'foto_principal': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

class RetiradaItemForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1, label="Quantidade a ser Retirada", widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...', 'placeholder': 'Ex: 10'}))

class AdicaoItemForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1, label="Quantidade a ser Adicionada", widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...', 'placeholder': 'Ex: 25'}))


class RecebimentoForm(forms.ModelForm):
    class Meta:
        model = Recebimento
        # ADICIONAMOS 'status' À LISTA DE CAMPOS
        fields = ['numero_nota_fiscal', 'fornecedor', 'setor', 'status', 'foto_documento', 'foto_embalagem', 'observacoes']
        
        widgets = {
            'numero_nota_fiscal': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'fornecedor': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'setor': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            
            # ADICIONAMOS O WIDGET PARA O CAMPO DE STATUS
            'status': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),

            'observacoes': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 3}),
            'foto_documento': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'foto_embalagem': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

class ProdutoFabricadoForm(forms.ModelForm):
    class Meta:
        model = ProdutoFabricado
        fields = ['nome', 'descricao', 'foto_principal']
        # Adicionando os widgets com as classes de estilo
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'descricao': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 4}),
            'foto_principal': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = ['item_estoque', 'quantidade_necessaria']
        # Adicionando rótulos personalizados
        labels = {
            'item_estoque': 'Componente',
            'quantidade_necessaria': 'Qtd. Necessária',
        }
        widgets = {
            'item_estoque': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
            'quantidade_necessaria': forms.NumberInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
        }

class DocumentoProdutoForm(forms.ModelForm):
    class Meta:
        model = DocumentoProdutoFabricado
        fields = ['documento', 'tipo']
        # Adicionando rótulos personalizados
        labels = {
            'documento': 'Arquivo',
            'tipo': 'Tipo de Documento',
        }
        widgets = {
            'documento': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 ...'}),
            'tipo': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm ...'}),
        }

class ProducaoForm(forms.Form):
    quantidade_a_produzir = forms.IntegerField(
        min_value=1,
        label="Quantidade a Produzir",
        initial=1, # Valor inicial
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
    )

class ImagemProdutoForm(forms.ModelForm):
    class Meta:
        model = ImagemProdutoFabricado
        fields = ['imagem']
        widgets = {
            'imagem': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            })
        }