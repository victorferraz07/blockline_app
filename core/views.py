from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required

from .models import (
    ItemEstoque, ProdutoFabricado, Recebimento, 
    DocumentoProdutoFabricado, Componente, Setor, Fornecedor,
    ImagemProdutoFabricado, ImagemItemEstoque, ItemFornecedor, Expedicao, ItemExpedido, DocumentoExpedicao, ImagemExpedicao,
    Empresa, PerfilUsuario 
)
from .forms import (
    ItemEstoqueForm, RetiradaItemForm, AdicaoItemForm, RecebimentoForm, 
    ProdutoFabricadoForm, DocumentoProdutoForm, ComponenteForm, ProducaoForm,
    ImagemProdutoForm, ItemFornecedorForm, ExpedicaoForm, ItemExpedidoForm, DocumentoExpedicaoForm, ImagemExpedicaoForm
)

def get_empresas_permitidas(user):
    if user.is_superuser:
        return Empresa.objects.all()
    try:
        if hasattr(user, 'perfil'):
            return user.perfil.empresas_permitidas.all()
    except PerfilUsuario.DoesNotExist:
        pass
    return Empresa.objects.none()

# core/views.py
@login_required
def dashboard(request):
    # A LINHA QUE ESTAVA FALTANDO:
    # Primeiro, nós chamamos nossa função auxiliar para obter a lista de empresas permitidas.
    empresas_permitidas = get_empresas_permitidas(request.user)
    
    total_itens_estoque = ItemEstoque.objects.count()
    total_produtos_fabricados = ProdutoFabricado.objects.count()
    
    # Agora, a variável 'empresas_permitidas' existe e pode ser usada nos filtros.
    ultimos_recebimentos = Recebimento.objects.filter(empresa__in=empresas_permitidas).order_by('-data_recebimento')[:5]
    ultimas_expedicoes = Expedicao.objects.filter(empresa__in=empresas_permitidas).order_by('-data_expedicao')[:5]

    contexto = {
        'total_itens_estoque': total_itens_estoque,
        'total_produtos_fabricados': total_produtos_fabricados,
        'ultimos_recebimentos': ultimos_recebimentos,
        'ultimas_expedicoes': ultimas_expedicoes,
    }
    return render(request, 'core/dashboard.html', contexto)

# --- Views de Estoque ---
@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
@permission_required('core.delete_itemestoque', raise_exception=True)
def excluir_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        nome_item = item.nome
        item.delete()
        messages.success(request, f'Item "{nome_item}" foi excluído com sucesso.')
        return redirect('lista_estoque')
    return redirect('gerenciar_item', pk=pk)

# --- Views de Recebimento ---

@login_required
@permission_required('core.view_recebimento', raise_exception=True)
def lista_recebimentos(request):
    query = request.GET.get('q')
    recebimentos = Recebimento.objects.all().order_by('-data_recebimento')
    if query:
        recebimentos = recebimentos.filter(Q(numero_nota_fiscal__icontains=query) | Q(fornecedor__icontains=query) | Q(usuario__username__icontains=query) | Q(setor__nome__icontains=query))
    contexto = {'recebimentos': recebimentos, 'query': query}
    return render(request, 'core/lista_recebimentos.html', contexto)

@login_required
# @permission_required('core.add_recebimento', raise_exception=True)
def registrar_recebimento(request):
    empresas_permitidas = get_empresas_permitidas(request.user)
    num_empresas = empresas_permitidas.count()

    if request.method == 'POST':
        form = RecebimentoForm(request.POST, request.FILES)
        # Se o usuário não for superusuário, a 'empresa' não será validada pelo form principal
        if not request.user.is_superuser and 'empresa' in form.fields:
            del form.fields['empresa']

        if form.is_valid():
            recebimento = form.save(commit=False)
            
            # LÓGICA DE ATRIBUIÇÃO FINAL:
            if request.user.is_superuser:
                # O superusuário escolheu no formulário, o form.save() já cuida disso.
                pass
            elif num_empresas == 1:
                # Se o usuário tem apenas uma empresa, atribuímos ela automaticamente.
                recebimento.empresa = empresas_permitidas.first()
            elif num_empresas > 1:
                # Se ele tem várias, o valor veio do formulário. Mas precisamos pegar o ID do POST.
                empresa_id = request.POST.get('empresa')
                if empresa_id:
                    recebimento.empresa_id = empresa_id
            else:
                messages.error(request, "Você não está associado a nenhuma empresa.")
                return redirect('dashboard')

            recebimento.usuario = request.user
            recebimento.save()
            messages.success(request, 'Recebimento registrado com sucesso!')
            return redirect('lista_recebimentos')
    else:
        form = RecebimentoForm()
        
        # LÓGICA DE EXIBIÇÃO FINAL:
        if not request.user.is_superuser:
            if num_empresas > 1:
                # Se ele pode ver várias, filtramos o dropdown para mostrar APENAS as permitidas.
                form.fields['empresa'].queryset = empresas_permitidas
            else:
                # Se ele pode ver 0 ou 1, não mostramos o campo.
                if 'empresa' in form.fields:
                    del form.fields['empresa']

    contexto = {
        'form': form,
        'titulo': 'Registrar Novo Recebimento',
        'ultimos_recebimentos': Recebimento.objects.filter(empresa__in=empresas_permitidas).order_by('-data_recebimento')[:5]
    }
    return render(request, 'core/registrar_recebimento.html', contexto)

@login_required
@permission_required('core.view_recebimento', raise_exception=True)
def detalhe_recebimento(request, pk):
    empresas_permitidas = get_empresas_permitidas(request.user)
    recebimento = get_object_or_404(Recebimento, pk=pk)
    contexto = {'recebimento': recebimento}

    return render(request, 'core/detalhe_recebimento.html', contexto)

@login_required
@permission_required('core.change_recebimento', raise_exception=True)
def editar_recebimento(request, pk):
    recebimento = get_object_or_404(Recebimento, pk=pk)
    if request.method == 'POST':
        post_data = request.POST.copy()
        fornecedor_val = post_data.get('fornecedor')
        if fornecedor_val and not fornecedor_val.isnumeric():
            novo_fornecedor, created = Fornecedor.objects.get_or_create(nome=fornecedor_val)
            post_data['fornecedor'] = novo_fornecedor.pk
        form = RecebimentoForm(post_data, request.FILES, instance=recebimento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recebimento atualizado com sucesso!')
            return redirect('lista_recebimentos')
    else:
        form = RecebimentoForm(instance=recebimento)
        
    contexto = {
        'form': form,
        'titulo': f'Editar Recebimento (NF: {recebimento.numero_nota_fiscal})',
        'is_editing': True,
        'recebimento': recebimento # Garante que o objeto está disponível
    }
    return render(request, 'core/registrar_recebimento.html', contexto)

# --- Views de Produtos Fabricados ---

@login_required
def lista_produtos(request):
    produtos = ProdutoFabricado.objects.select_related('item_associado').all().order_by('nome')

    contexto = {
        'produtos': produtos
    }
    return render(request, 'core/lista_produtos.html', contexto)

@login_required
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

@login_required
def adicionar_produto(request):
    DocumentoFormSet = modelformset_factory(DocumentoProdutoFabricado, form=DocumentoProdutoForm, extra=1, can_delete=False)
    
    if request.method == 'POST':
        form = ProdutoFabricadoForm(request.POST, request.FILES)
        formset = DocumentoFormSet(request.POST, request.FILES, queryset=DocumentoProdutoFabricado.objects.none())

        if form.is_valid() and formset.is_valid():
            produto_base = form.save(commit=False)
            
            # Criamos o item de estoque associado
            item_estoque_associado = ItemEstoque.objects.create(
                nome=produto_base.nome,
                descricao=f"Produto acabado: {produto_base.descricao}",
                tipo='produto_acabado',
                is_produto_fabricado=True,
                # A LINHA DA CORREÇÃO ESTÁ AQUI:
                # Copiamos a foto do formulário do produto para o novo item de estoque.
                foto_principal=produto_base.foto_principal 
            )
            
            # Agora, linkamos os dois e salvamos o produto
            produto_base.item_associado = item_estoque_associado
            produto_base.save()
            
            # ... (resto da lógica para salvar os documentos)
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

@login_required
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

@login_required
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

# --- Views da Expedição ---

@login_required
def lista_expedicoes(request):
    expedicoes = Expedicao.objects.all().order_by('-data_expedicao')
    return render(request, 'core/lista_expedicoes.html', {'expedicoes': expedicoes})

@login_required
def detalhe_expedicao(request, pk):
    expedicao = get_object_or_404(Expedicao, pk=pk)
    return render(request, 'core/detalhe_expedicao.html', {'expedicao': expedicao})

@login_required
@transaction.atomic
def registrar_expedicao(request):
    ItemExpedidoFormSet = inlineformset_factory(Expedicao, ItemExpedido, form=ItemExpedidoForm, extra=1, can_delete=False)
    DocumentoExpedicaoFormSet = inlineformset_factory(Expedicao, DocumentoExpedicao, form=DocumentoExpedicaoForm, extra=1, can_delete=False)
    ImagemExpedicaoFormSet = inlineformset_factory(Expedicao, ImagemExpedicao, form=ImagemExpedicaoForm, extra=1, can_delete=False)

    if request.method == 'POST':
        form = ExpedicaoForm(request.POST, request.FILES)
        item_formset = ItemExpedidoFormSet(request.POST, prefix='itens')
        documento_formset = DocumentoExpedicaoFormSet(request.POST, request.FILES, prefix='documentos')
        imagem_formset = ImagemExpedicaoFormSet(request.POST, request.FILES, prefix='imagens')

        if form.is_valid() and item_formset.is_valid() and documento_formset.is_valid() and imagem_formset.is_valid():
            
            # --- Verificação de Estoque ---
            pode_prosseguir = True
            for form_item in item_formset:
                if form_item.cleaned_data and form_item.cleaned_data.get('produto'):
                    produto = form_item.cleaned_data['produto']
                    quantidade = form_item.cleaned_data['quantidade']
                    if quantidade > produto.item_associado.quantidade:
                        messages.error(request, f"Estoque insuficiente para {produto.nome}. Disponível: {produto.item_associado.quantidade}")
                        pode_prosseguir = False
            
            if not pode_prosseguir:
                # Se não puder prosseguir, renderiza a página de novo com os erros
                contexto = {'form': form, 'item_formset': item_formset, 'documento_formset': documento_formset, 'imagem_formset': imagem_formset}
                return render(request, 'core/registrar_expedicao.html', contexto)
            
            # --- Se tudo estiver OK, salva e dá baixa no estoque ---
            expedicao = form.save(commit=False)
            expedicao.usuario = request.user
            expedicao.save()

            item_formset.instance = expedicao
            item_formset.save()

            documento_formset.instance = expedicao
            documento_formset.save()
            
            imagem_formset.instance = expedicao
            imagem_formset.save()
            
            # Baixa no estoque
            for form_item in item_formset:
                if form_item.cleaned_data and form_item.cleaned_data.get('produto'):
                    produto = form_item.cleaned_data['produto']
                    quantidade = form_item.cleaned_data['quantidade']
                    produto.item_associado.quantidade -= quantidade
                    produto.item_associado.save()

            messages.success(request, f"Expedição #{expedicao.pk} registrada com sucesso!")
            return redirect('lista_expedicoes')
    else:
        form = ExpedicaoForm()
        item_formset = ItemExpedidoFormSet(prefix='itens')
        documento_formset = DocumentoExpedicaoFormSet(prefix='documentos')
        imagem_formset = ImagemExpedicaoFormSet(prefix='imagens')

    contexto = {
        'form': form,
        'item_formset': item_formset,
        'documento_formset': documento_formset,
        'imagem_formset': imagem_formset,
        'titulo': 'Registrar Nova Expedição'
    }
    return render(request, 'core/registrar_expedicao.html', contexto)

@login_required
def editar_expedicao(request, pk):
    expedicao = get_object_or_404(Expedicao, pk=pk)
    
    ItemExpedidoFormSet = inlineformset_factory(Expedicao, ItemExpedido, form=ItemExpedidoForm, extra=1, can_delete=True)
    DocumentoExpedicaoFormSet = inlineformset_factory(Expedicao, DocumentoExpedicao, form=DocumentoExpedicaoForm, extra=1, can_delete=True)
    ImagemExpedicaoFormSet = inlineformset_factory(Expedicao, ImagemExpedicao, form=ImagemExpedicaoForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = ExpedicaoForm(request.POST, instance=expedicao)
        item_formset = ItemExpedidoFormSet(request.POST, instance=expedicao, prefix='itens')
        documento_formset = DocumentoExpedicaoFormSet(request.POST, request.FILES, instance=expedicao, prefix='documentos')
        imagem_formset = ImagemExpedicaoFormSet(request.POST, request.FILES, instance=expedicao, prefix='imagens')

        if form.is_valid() and item_formset.is_valid() and documento_formset.is_valid() and imagem_formset.is_valid():
            form.save()
            item_formset.save()
            documento_formset.save()
            imagem_formset.save()
            
            messages.success(request, f"Expedição #{expedicao.pk} atualizada com sucesso!")
            return redirect('detalhe_expedicao', pk=expedicao.pk)
    else:
        form = ExpedicaoForm(instance=expedicao)
        item_formset = ItemExpedidoFormSet(instance=expedicao, prefix='itens')
        documento_formset = DocumentoExpedicaoFormSet(instance=expedicao, prefix='documentos')
        imagem_formset = ImagemExpedicaoFormSet(instance=expedicao, prefix='imagens')

    contexto = {
        'titulo': f'Editando Expedição #{expedicao.pk}',
        'expedicao': expedicao,
        'form': form,
        'item_formset': item_formset,
        'documento_formset': documento_formset,
        'imagem_formset': imagem_formset
    }
    return render(request, 'core/editar_expedicao.html', contexto)

@login_required
@permission_required('core.delete_recebimento', raise_exception=True)
def excluir_recebimento(request, pk):
    recebimento = get_object_or_404(Recebimento, pk=pk)
    if request.method == 'POST':
        recebimento.delete()
        messages.success(request, f"Registro de recebimento #{pk} foi excluído com sucesso.")
        return redirect('lista_recebimentos')
    # Se não for POST, apenas redireciona de volta para os detalhes
    return redirect('detalhe_recebimento', pk=pk)

@login_required
def excluir_produto(request, pk):
    produto = get_object_or_404(ProdutoFabricado, pk=pk)
    if request.method == 'POST':
        # Antes de deletar o produto, deletamos o item de estoque associado
        if produto.item_associado:
            produto.item_associado.delete()

        nome_produto = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome_produto}" foi excluído com sucesso.')
        return redirect('lista_produtos')

    return redirect('detalhe_produto', pk=pk)

@login_required
def excluir_expedicao(request, pk):
    expedicao = get_object_or_404(Expedicao, pk=pk)
    if request.method == 'POST':
        expedicao.delete()
        messages.success(request, f"Expedição #{pk} foi excluída com sucesso.")
        return redirect('lista_expedicoes')
    
    return redirect('detalhe_expedicao', pk=pk)