from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import ItemEstoque, ProdutoFabricado, Recebimento, SaidaProduto
from .forms import ItemEstoqueForm, RetiradaItemForm, AdicaoItemForm, RecebimentoForm

def dashboard(request):
    total_itens_estoque = ItemEstoque.objects.count()
    total_produtos_fabricados = ProdutoFabricado.objects.count()
    ultimos_recebimentos = Recebimento.objects.order_by('-data_recebimento')[:5]
    ultimas_saidas = SaidaProduto.objects.order_by('-data_saida')[:5]
    contexto = {
        'total_itens_estoque': total_itens_estoque,
        'total_produtos_fabricados': total_produtos_fabricados,
        'ultimos_recebimentos': ultimos_recebimentos,
        'ultimas_saidas': ultimas_saidas,
    }
    return render(request, 'core/dashboard.html', contexto)

# --- Views de Estoque ---

def lista_estoque(request):
    query = request.GET.get('q')
    itens = ItemEstoque.objects.all().order_by('nome')
    if query:
        itens = itens.filter(
            Q(nome__icontains=query) | Q(descricao__icontains=query)
        )
    total_itens = itens.count()
    itens_esgotados = itens.filter(quantidade=0).count()
    itens_em_baixo_estoque = itens.filter(quantidade__gt=0, quantidade__lte=10).count()
    contexto = {
        'itens': itens,
        'total_itens': total_itens,
        'itens_esgotados': itens_esgotados,
        'itens_em_baixo_estoque': itens_em_baixo_estoque,
        'query': query,
    }
    return render(request, 'core/lista_estoque.html', contexto)

def adicionar_item(request):
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo item adicionado com sucesso!')
            return redirect('lista_estoque')
    else:
        form = ItemEstoqueForm()
    contexto = {
        'form': form,
        'titulo': 'Adicionar Novo Item ao Estoque'
    }
    return render(request, 'core/adicionar_item.html', contexto)

def gerenciar_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Item "{item.nome}" atualizado com sucesso.')
            return redirect('gerenciar_item', pk=item.pk)
    else:
        form = ItemEstoqueForm(instance=item)
    contexto = {
        'form': form,
        'item': item,
        'retirada_form': RetiradaItemForm(),
        'adicao_form': AdicaoItemForm(),
    }
    return render(request, 'core/gerenciar_item.html', contexto)

def retirar_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        form = RetiradaItemForm(request.POST)
        if form.is_valid():
            quantidade_a_retirar = form.cleaned_data['quantidade']
            if quantidade_a_retirar > item.quantidade:
                messages.error(request, f'Não é possível retirar {quantidade_a_retirar}. Quantidade em estoque: {item.quantidade}.')
            else:
                item.quantidade -= quantidade_a_retirar
                item.save()
                messages.success(request, f'{quantidade_a_retirar} unidade(s) de {item.nome} retiradas com sucesso.')
    return redirect('gerenciar_item', pk=item.pk)

def adicionar_estoque(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        form = AdicaoItemForm(request.POST)
        if form.is_valid():
            quantidade_a_adicionar = form.cleaned_data['quantidade']
            item.quantidade += quantidade_a_adicionar
            item.save()
            messages.success(request, f'{quantidade_a_adicionar} unidade(s) de {item.nome} adicionadas com sucesso.')
    return redirect('gerenciar_item', pk=item.pk)

def excluir_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        nome_item = item.nome
        item.delete()
        messages.success(request, f'Item "{nome_item}" foi excluído com sucesso.')
        return redirect('lista_estoque')
    return redirect('gerenciar_item', pk=pk)

# --- Views de Recebimento ---

def lista_recebimentos(request):
    query = request.GET.get('q')
    recebimentos = Recebimento.objects.all().order_by('-data_recebimento')
    if query:
        recebimentos = recebimentos.filter(
            Q(numero_nota_fiscal__icontains=query) |
            Q(fornecedor__icontains=query) |
            Q(usuario__username__icontains=query) |
            Q(setor__nome__icontains=query)
        )
    # A correção do erro 'NameError' está aqui:
    contexto = {
        'recebimentos': recebimentos,
        'query': query
    }
    return render(request, 'core/lista_recebimentos.html', contexto)

def registrar_recebimento(request):
    if request.method == 'POST':
        form = RecebimentoForm(request.POST, request.FILES)
        if form.is_valid():
            recebimento = form.save(commit=False)
            recebimento.usuario = request.user
            recebimento.save()
            messages.success(request, 'Recebimento registrado com sucesso!')
            return redirect('lista_recebimentos')
    else:
        form = RecebimentoForm()
    ultimos_recebimentos = Recebimento.objects.order_by('-data_recebimento')[:5]
    contexto = {
        'form': form,
        'titulo': 'Registrar Novo Recebimento',
        'ultimos_recebimentos': ultimos_recebimentos
    }
    return render(request, 'core/registrar_recebimento.html', contexto)

def detalhe_recebimento(request, pk):
    recebimento = get_object_or_404(Recebimento, pk=pk)
    contexto = {
        'recebimento': recebimento
    }
    return render(request, 'core/detalhe_recebimento.html', contexto)

def editar_recebimento(request, pk):
    recebimento = get_object_or_404(Recebimento, pk=pk)
    if request.method == 'POST':
        form = RecebimentoForm(request.POST, request.FILES, instance=recebimento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recebimento atualizado com sucesso!')
            return redirect('lista_recebimentos')
    else:
        form = RecebimentoForm(instance=recebimento)
    contexto = {
        'form': form,
        'titulo': f'Editar Recebimento (NF: {recebimento.numero_nota_fiscal})',
        'is_editing': True
    }
    return render(request, 'core/registrar_recebimento.html', contexto)