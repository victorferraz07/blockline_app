from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory, inlineformset_factory
from .models import (
    ItemEstoque, ProdutoFabricado, Recebimento, SaidaProduto, 
    DocumentoProdutoFabricado, Componente, Setor, Fornecedor,
    ImagemProdutoFabricado, ImagemItemEstoque, ItemFornecedor
)
from .forms import (
    ItemEstoqueForm, RetiradaItemForm, AdicaoItemForm, RecebimentoForm, 
    ProdutoFabricadoForm, DocumentoProdutoForm, ComponenteForm, ProducaoForm,
    ImagemProdutoForm, ItemFornecedorForm
)


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
        itens = itens.filter(Q(nome__icontains=query) | Q(descricao__icontains=query))
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
    contexto = {'form': form, 'titulo': 'Adicionar Novo Item ao Estoque'}
    return render(request, 'core/adicionar_item.html', contexto)

def gerenciar_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    FornecedorItemFormSet = inlineformset_factory(ItemEstoque, ItemFornecedor, form=ItemFornecedorForm, extra=1, can_delete=True)

    if request.method == 'POST':
        post_data = request.POST.copy()
        total_forms = int(post_data.get('fornecedores-TOTAL_FORMS', 0))
        for i in range(total_forms):
            field_name = f'fornecedores-{i}-fornecedor'
            fornecedor_val = post_data.get(field_name)
            if fornecedor_val and not fornecedor_val.isnumeric():
                novo_fornecedor, created = Fornecedor.objects.get_or_create(nome=fornecedor_val)
                post_data[field_name] = novo_fornecedor.pk

        form = ItemEstoqueForm(request.POST, request.FILES, instance=item)
        formset_fornecedores = FornecedorItemFormSet(post_data, instance=item, prefix='fornecedores')
        
        if form.is_valid() and formset_fornecedores.is_valid():
            form.save()
            formset_fornecedores.save()
            messages.success(request, 'Item atualizado com sucesso!')
            return redirect('gerenciar_item', pk=item.pk)
    else:
        form = ItemEstoqueForm(instance=item)
        formset_fornecedores = FornecedorItemFormSet(instance=item, prefix='fornecedores')

    contexto = {
        'form': form,
        'item': item,
        'formset_fornecedores': formset_fornecedores,
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
        recebimentos = recebimentos.filter(Q(numero_nota_fiscal__icontains=query) | Q(fornecedor__icontains=query) | Q(usuario__username__icontains=query) | Q(setor__nome__icontains=query))
    contexto = {'recebimentos': recebimentos, 'query': query}
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
    contexto = {'form': form, 'titulo': 'Registrar Novo Recebimento', 'ultimos_recebimentos': ultimos_recebimentos}
    return render(request, 'core/registrar_recebimento.html', contexto)

def detalhe_recebimento(request, pk):
    recebimento = get_object_or_404(Recebimento, pk=pk)
    contexto = {'recebimento': recebimento}
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
    contexto = {'form': form, 'titulo': f'Editar Recebimento (NF: {recebimento.numero_nota_fiscal})', 'is_editing': True}
    return render(request, 'core/registrar_recebimento.html', contexto)

# --- Views de Produtos Fabricados ---

def lista_produtos(request):
    produtos = ProdutoFabricado.objects.select_related('item_associado').all().order_by('nome')

    contexto = {
        'produtos': produtos
    }
    return render(request, 'core/lista_produtos.html', contexto)

def detalhe_produto(request, pk):
    produto = get_object_or_404(ProdutoFabricado, pk=pk)
    componentes = produto.componente_set.all()

    # Lógica do Simulador
    form = ProducaoForm(request.GET or None)
    qtd_a_produzir = 1 # Valor padrão
    if form.is_valid():
        qtd_a_produzir = form.cleaned_data['quantidade_a_produzir']

    # Adicionando os cálculos a cada componente
    for componente in componentes:
        componente.total_necessario = componente.quantidade_necessaria * qtd_a_produzir
        componente.estoque_suficiente = componente.item_estoque.quantidade >= componente.total_necessario

    contexto = {
        'produto': produto,
        'componentes': componentes,
        'producao_form': form, # Enviamos o formulário para o template
        'qtd_a_produzir': qtd_a_produzir # E a quantidade para exibição
    }
    return render(request, 'core/detalhe_produto.html', contexto)

def adicionar_produto(request):
    DocumentoFormSet = modelformset_factory(DocumentoProdutoFabricado, form=DocumentoProdutoForm, extra=1, can_delete=False)
    if request.method == 'POST':
        form = ProdutoFabricadoForm(request.POST, request.FILES)
        formset = DocumentoFormSet(request.POST, request.FILES, queryset=DocumentoProdutoFabricado.objects.none())
        if form.is_valid() and formset.is_valid():
            produto_base = form.save(commit=False)
            # Precisamos criar o item de estoque associado antes de salvar o produto
            item_estoque_associado = ItemEstoque.objects.create(
                nome=produto_base.nome,
                descricao=f"Produto acabado: {produto_base.descricao}",
                tipo='produto_acabado',
                is_produto_fabricado=True
            )
            produto_base.item_associado = item_estoque_associado
            produto_base.save()
            for doc_form in formset:
                if doc_form.cleaned_data and doc_form.cleaned_data.get('documento'):
                    documento = doc_form.save(commit=False)
                    documento.produto = produto_base
                    documento.save()
            messages.success(request, f'Produto "{produto_base.nome}" e seus documentos foram criados com sucesso!')
            return redirect('lista_produtos')
    else:
        form = ProdutoFabricadoForm()
        formset = DocumentoFormSet(queryset=DocumentoProdutoFabricado.objects.none())
    contexto = {'form': form, 'formset': formset, 'titulo': 'Criar Novo Produto'}
    return render(request, 'core/form_produto.html', contexto)

def editar_produto(request, pk):
    produto = get_object_or_404(ProdutoFabricado, pk=pk)
    
    ComponenteFormSet = inlineformset_factory(ProdutoFabricado, Componente, form=ComponenteForm, extra=0, can_delete=True)
    DocumentoFormSet = inlineformset_factory(ProdutoFabricado, DocumentoProdutoFabricado, form=DocumentoProdutoForm, extra=0, can_delete=True)
    ImagemFormSet = inlineformset_factory(ProdutoFabricado, ImagemProdutoFabricado, form=ImagemProdutoForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = ProdutoFabricadoForm(request.POST, request.FILES, instance=produto)
        componente_formset = ComponenteFormSet(request.POST, instance=produto, prefix='componentes')
        documento_formset = DocumentoFormSet(request.POST, request.FILES, instance=produto, prefix='documentos')
        imagem_formset = ImagemFormSet(request.POST, request.FILES, instance=produto, prefix='imagens')

        if form.is_valid() and componente_formset.is_valid() and documento_formset.is_valid() and imagem_formset.is_valid():
            form.save()
            componente_formset.save()
            documento_formset.save()
            imagem_formset.save()
            
            messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso!')
            return redirect('detalhe_produto', pk=produto.pk)
    else:
        form = ProdutoFabricadoForm(instance=produto)
        componente_formset = ComponenteFormSet(instance=produto, prefix='componentes')
        documento_formset = DocumentoFormSet(instance=produto, prefix='documentos')
        imagem_formset = ImagemFormSet(instance=produto, prefix='imagens')

    contexto = {
        'form': form,
        'componente_formset': componente_formset,
        'documento_formset': documento_formset,
        'imagem_formset': imagem_formset,
        'produto': produto,
    }
    return render(request, 'core/editar_produto.html', contexto)

@transaction.atomic
def finalizar_producao(request, pk):
    produto = get_object_or_404(ProdutoFabricado, pk=pk)
    if request.method == 'POST':
        form = ProducaoForm(request.POST)
        if form.is_valid():
            qtd_a_produzir = form.cleaned_data['quantidade_a_produzir']
            componentes_insuficientes = []
            for componente in produto.componente_set.all():
                total_necessario = componente.quantidade_necessaria * qtd_a_produzir
                if componente.item_estoque.quantidade < total_necessario:
                    componentes_insuficientes.append(componente.item_estoque.nome)
            if componentes_insuficientes:
                msg_erro = f'Produção não pode ser iniciada. Estoque insuficiente para: {", ".join(componentes_insuficientes)}.'
                messages.error(request, msg_erro)
                return redirect('detalhe_produto', pk=pk)
            for componente in produto.componente_set.all():
                componente.item_estoque.quantidade -= componente.quantidade_necessaria * qtd_a_produzir
                componente.item_estoque.save()
            if hasattr(produto, 'item_associado') and produto.item_associado:
                produto.item_associado.quantidade += qtd_a_produzir
                produto.item_associado.save()
            else:
                messages.error(request, f'Erro crítico: O produto "{produto.nome}" não está associado a um item de estoque.')
                return redirect('detalhe_produto', pk=pk)
            messages.success(request, f'{qtd_a_produzir} unidade(s) de "{produto.nome}" foram produzidas e adicionadas ao estoque!')
            return redirect('detalhe_produto', pk=pk)
    return redirect('detalhe_produto', pk=pk)