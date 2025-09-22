# core/forms.py
from django import forms
from .models import ItemEstoque, Recebimento

# Formulário para CRIAR e EDITAR um Item de Estoque
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

# Formulário para a AÇÃO de RETIRADA
class RetiradaItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade a ser Retirada",
        widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'placeholder': 'Ex: 10'})
    )

# Formulário para a AÇÃO de ADIÇÃO
class AdicaoItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade a ser Adicionada",
        widget=forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'placeholder': 'Ex: 25'})
    )

# Formulário para registrar um novo RECEBIMENTO
class RecebimentoForm(forms.ModelForm):
    class Meta:
        model = Recebimento
        fields = ['descricao_pacote', 'setor', 'foto_documento', 'foto_embalagem', 'observacoes']
        widgets = {
            'descricao_pacote': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 3}),
            'setor': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'observacoes': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 3}),
        }