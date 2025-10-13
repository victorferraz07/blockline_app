from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Sum, Avg
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
import json

from .models import (
    ItemEstoque, ProdutoFabricado, Recebimento,
    DocumentoProdutoFabricado, Componente, Setor, Fornecedor,
    ImagemProdutoFabricado, ImagemItemEstoque, ItemFornecedor, Expedicao, ItemExpedido, DocumentoExpedicao, ImagemExpedicao,
    Empresa, PerfilUsuario,
    KanbanColumn, Task, TaskQuantidadeFeita, TaskHistorico,
    JornadaTrabalho, RegistroPonto, ResumoMensal, AbonoDia,
    MovimentacaoEstoque, Cliente,
)
from .forms import (
    ItemEstoqueForm, RetiradaItemForm, AdicaoItemForm, RecebimentoForm,
    ProdutoFabricadoForm, DocumentoProdutoForm, ComponenteForm, ProducaoForm,
    ImagemProdutoForm, ItemFornecedorForm, ExpedicaoForm, ItemExpedidoForm, DocumentoExpedicaoForm, ImagemExpedicaoForm,
    ClienteForm, FornecedorForm
)
from .decorators import superuser_required, filter_by_empresa, get_user_empresa

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
    from django.db.models import Sum
    from datetime import datetime, timedelta

    # Estatísticas gerais
    total_itens_estoque = ItemEstoque.objects.count()
    total_produtos_fabricados = ProdutoFabricado.objects.count()
    total_recebimentos = Recebimento.objects.count()
    total_expedicoes = Expedicao.objects.count()

    # Quantidade total em estoque
    quantidade_total_estoque = ItemEstoque.objects.aggregate(total=Sum('quantidade'))['total'] or 0

    # Atividades recentes
    ultimos_recebimentos = Recebimento.objects.order_by('-data_recebimento')[:5]
    ultimas_expedicoes = Expedicao.objects.order_by('-data_expedicao')[:5]

    # Combinar e ordenar atividades por data
    atividades = []

    for recebimento in ultimos_recebimentos:
        atividades.append({
            'tipo': 'recebimento',
            'data': recebimento.data_recebimento,
            'objeto': recebimento
        })

    for expedicao in ultimas_expedicoes:
        atividades.append({
            'tipo': 'expedicao',
            'data': expedicao.data_expedicao,
            'objeto': expedicao
        })

    # Ordenar por data (mais recente primeiro)
    atividades.sort(key=lambda x: x['data'], reverse=True)
    atividades = atividades[:10]  # Limitar a 10 atividades

    contexto = {
        'total_itens_estoque': total_itens_estoque,
        'total_produtos_fabricados': total_produtos_fabricados,
        'total_recebimentos': total_recebimentos,
        'total_expedicoes': total_expedicoes,
        'quantidade_total_estoque': quantidade_total_estoque,
        'atividades': atividades,
    }
    return render(request, 'core/dashboard.html', contexto)

# --- Views de Estoque ---
@login_required
def lista_estoque(request):
    # SEGURANÇA: Filtrar apenas itens da empresa do usuário
    itens = ItemEstoque.objects.all()
    # Nota: ItemEstoque não tem campo empresa, então mostra todos
    # Se precisar filtro por empresa, adicione campo empresa ao modelo

    # Busca funcional
    query = request.GET.get('q', '').strip()
    if query:
        itens = itens.filter(
            Q(nome__icontains=query) |
            Q(descricao__icontains=query) |
            Q(tipo__icontains=query)
        )

    # Filtro por tipo
    tipo_filtro = request.GET.get('tipo', '').strip()
    if tipo_filtro:
        itens = itens.filter(tipo=tipo_filtro)

    # Ordenação
    ordenacao = request.GET.get('ordenar', 'nome')
    if ordenacao == 'nome':
        itens = itens.order_by('nome')
    elif ordenacao == 'estoque_asc':
        itens = itens.order_by('quantidade', 'nome')
    elif ordenacao == 'estoque_desc':
        itens = itens.order_by('-quantidade', 'nome')
    elif ordenacao == 'tipo':
        itens = itens.order_by('tipo', 'nome')
    elif ordenacao == 'data_desc':
        itens = itens.order_by('-id')
    else:
        itens = itens.order_by('nome')

    # Estatísticas
    total_itens = itens.count()
    itens_esgotados = itens.filter(quantidade=0).count()
    itens_saudaveis = itens.filter(quantidade__gte=10).count()

    contexto = {
        'itens': itens,
        'total_itens': total_itens,
        'itens_esgotados': itens_esgotados,
        'itens_saudaveis': itens_saudaveis,
        'query': query,
        'ordenacao': ordenacao,
        'tipo_filtro': tipo_filtro,
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
    from datetime import timedelta

    item = get_object_or_404(ItemEstoque, pk=pk)
    FornecedorItemFormSet = inlineformset_factory(ItemEstoque, ItemFornecedor, form=ItemFornecedorForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES, instance=item)
        formset_fornecedores = FornecedorItemFormSet(request.POST, instance=item, prefix='fornecedores')

        if form.is_valid() and formset_fornecedores.is_valid():
            form.save()
            formset_fornecedores.save()
            messages.success(request, 'Item atualizado com sucesso!')
            return redirect('gerenciar_item', pk=item.pk)
        else:
            # Exibir erros de validação
            if not formset_fornecedores.is_valid():
                for form_error in formset_fornecedores.errors:
                    if form_error:
                        messages.error(request, f'Erro no formulário de fornecedores: {form_error}')
                for non_form_error in formset_fornecedores.non_form_errors():
                    messages.error(request, f'Erro: {non_form_error}')
    else:
        form = ItemEstoqueForm(instance=item)
        formset_fornecedores = FornecedorItemFormSet(instance=item, prefix='fornecedores')

    # Estatísticas e dados adicionais
    # 1. Valor total em estoque
    ultimo_preco = item.itemfornecedor_set.order_by('-data_cotacao').first()
    valor_total_estoque = 0
    if ultimo_preco:
        valor_total_estoque = item.quantidade * float(ultimo_preco.valor_pago)

    # 2. Custo médio unitário
    custo_medio = item.itemfornecedor_set.aggregate(media=Avg('valor_pago'))['media'] or 0

    # 3. Movimentações nos últimos 30 dias
    data_limite = timezone.now() - timedelta(days=30)
    movimentacoes_recentes = item.movimentacoes.filter(data_hora__gte=data_limite)
    total_entradas = movimentacoes_recentes.filter(tipo='entrada').aggregate(total=Sum('quantidade'))['total'] or 0
    total_saidas = movimentacoes_recentes.filter(tipo='saida').aggregate(total=Sum('quantidade'))['total'] or 0

    # 4. Histórico completo
    historico_movimentacoes = item.movimentacoes.all()[:20]  # Últimas 20 movimentações

    # 5. Galeria de imagens
    galeria_imagens = item.imagens.all()

    # 6. Dados para o gráfico de evolução (últimos 30 dias)
    evolucao_estoque = []
    for i in range(29, -1, -1):
        data = timezone.now() - timedelta(days=i)
        data_inicio = data.replace(hour=0, minute=0, second=0, microsecond=0)
        data_fim = data_inicio + timedelta(days=1)

        # Calcular estoque naquela data
        movimentacoes_ate_data = item.movimentacoes.filter(data_hora__lt=data_fim)
        entradas = movimentacoes_ate_data.filter(tipo='entrada').aggregate(total=Sum('quantidade'))['total'] or 0
        saidas = movimentacoes_ate_data.filter(tipo='saida').aggregate(total=Sum('quantidade'))['total'] or 0
        estoque_dia = entradas - saidas

        evolucao_estoque.append({
            'data': data.strftime('%d/%m'),
            'quantidade': estoque_dia
        })

    contexto = {
        'form': form,
        'item': item,
        'formset_fornecedores': formset_fornecedores,
        'retirada_form': RetiradaItemForm(),
        'adicao_form': AdicaoItemForm(),
        # Estatísticas
        'valor_total_estoque': valor_total_estoque,
        'custo_medio': custo_medio,
        'total_entradas_30d': total_entradas,
        'total_saidas_30d': total_saidas,
        # Histórico e galeria
        'historico_movimentacoes': historico_movimentacoes,
        'galeria_imagens': galeria_imagens,
        # Gráfico (convertido para JSON)
        'evolucao_estoque': json.dumps(evolucao_estoque),
    }
    return render(request, 'core/gerenciar_item.html', contexto)

@login_required
def retirar_item(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        form = RetiradaItemForm(request.POST)
        if form.is_valid():
            quantidade_a_retirar = form.cleaned_data['quantidade']
            observacoes = form.cleaned_data.get('observacoes', '')
            if quantidade_a_retirar > item.quantidade:
                messages.error(request, f'Não é possível retirar {quantidade_a_retirar}. Quantidade em estoque: {item.quantidade}.')
            else:
                item.quantidade -= quantidade_a_retirar
                item.save()

                # Registrar movimentação
                MovimentacaoEstoque.objects.create(
                    item=item,
                    tipo='saida',
                    quantidade=quantidade_a_retirar,
                    usuario=request.user,
                    observacoes=observacoes
                )

                messages.success(request, f'{quantidade_a_retirar} unidade(s) de {item.nome} retiradas com sucesso.')
    return redirect('gerenciar_item', pk=item.pk)

@login_required
def adicionar_estoque(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        form = AdicaoItemForm(request.POST)
        if form.is_valid():
            quantidade_a_adicionar = form.cleaned_data['quantidade']
            observacoes = form.cleaned_data.get('observacoes', '')
            item.quantidade += quantidade_a_adicionar
            item.save()

            # Registrar movimentação
            MovimentacaoEstoque.objects.create(
                item=item,
                tipo='entrada',
                quantidade=quantidade_a_adicionar,
                usuario=request.user,
                observacoes=observacoes
            )

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

@login_required
def duplicar_item(request, pk):
    from django.core.files.base import ContentFile
    import os

    item_original = get_object_or_404(ItemEstoque, pk=pk)

    # Gerar nome único para a cópia
    nome_base = f"{item_original.nome} (Cópia)"
    nome_final = nome_base
    contador = 1

    while ItemEstoque.objects.filter(nome=nome_final).exists():
        nome_final = f"{nome_base} {contador}"
        contador += 1

    # Criar cópia do item
    item_duplicado = ItemEstoque.objects.create(
        tipo=item_original.tipo,
        nome=nome_final,
        descricao=item_original.descricao,
        quantidade=0,  # Começa com quantidade zerada
        local_armazenamento=item_original.local_armazenamento,
        is_produto_fabricado=item_original.is_produto_fabricado
    )

    # Copiar foto principal se existir
    if item_original.foto_principal and os.path.exists(item_original.foto_principal.path):
        with open(item_original.foto_principal.path, 'rb') as f:
            item_duplicado.foto_principal.save(
                os.path.basename(item_original.foto_principal.name),
                ContentFile(f.read()),
                save=True
            )

    # Copiar documentação se existir
    if item_original.documentacao and os.path.exists(item_original.documentacao.path):
        with open(item_original.documentacao.path, 'rb') as f:
            item_duplicado.documentacao.save(
                os.path.basename(item_original.documentacao.name),
                ContentFile(f.read()),
                save=True
            )

    # Copiar fornecedores associados
    for item_fornecedor in item_original.itemfornecedor_set.all():
        ItemFornecedor.objects.create(
            item_estoque=item_duplicado,
            fornecedor=item_fornecedor.fornecedor,
            fornecedor_nome=item_fornecedor.fornecedor_nome,
            valor_pago=item_fornecedor.valor_pago,
            data_cotacao=item_fornecedor.data_cotacao
        )

    messages.success(request, f'Item "{item_duplicado.nome}" foi criado com sucesso!')
    return redirect('gerenciar_item', pk=item_duplicado.pk)


# --- Views de Recebimento ---

@login_required
@permission_required('core.view_recebimento', raise_exception=True)
def lista_recebimentos(request):
    from datetime import timedelta
    from decimal import Decimal

    query = request.GET.get('q', '')
    status_filtro = request.GET.get('status', '')
    ordenacao = request.GET.get('ordenar', 'data_desc')

    # Filtrar recebimentos
    recebimentos = Recebimento.objects.all()

    # Aplicar filtro de busca
    if query:
        recebimentos = recebimentos.filter(
            Q(numero_nota_fiscal__icontains=query) |
            Q(fornecedor__nome__icontains=query) |
            Q(usuario__username__icontains=query) |
            Q(setor__nome__icontains=query)
        )

    # Aplicar filtro de status
    if status_filtro:
        recebimentos = recebimentos.filter(status=status_filtro)

    # Aplicar ordenação
    if ordenacao == 'data_desc':
        recebimentos = recebimentos.order_by('-data_recebimento')
    elif ordenacao == 'data_asc':
        recebimentos = recebimentos.order_by('data_recebimento')
    elif ordenacao == 'fornecedor':
        recebimentos = recebimentos.order_by('fornecedor__nome')
    elif ordenacao == 'valor_desc':
        recebimentos = recebimentos.order_by('-valor_total')
    elif ordenacao == 'status':
        recebimentos = recebimentos.order_by('status')

    # Estatísticas
    total_recebimentos = Recebimento.objects.count()

    # Valor total do mês atual
    data_limite = timezone.now() - timedelta(days=30)
    recebimentos_mes = Recebimento.objects.filter(data_recebimento__gte=data_limite)
    valor_total_mes = recebimentos_mes.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')

    # Recebimentos aguardando
    aguardando_conferencia = Recebimento.objects.filter(status='aguardando').count()

    contexto = {
        'recebimentos': recebimentos,
        'query': query,
        'status_filtro': status_filtro,
        'ordenacao': ordenacao,
        'total_recebimentos': total_recebimentos,
        'valor_total_mes': valor_total_mes,
        'aguardando_conferencia': aguardando_conferencia,
    }
    return render(request, 'core/lista_recebimentos.html', contexto)

@login_required
# @permission_required('core.add_recebimento', raise_exception=True)
def registrar_recebimento(request):
    if request.method == 'POST':
        form = RecebimentoForm(request.POST, request.FILES)
        # Remover campo empresa do formulário (será atribuído automaticamente)
        if 'empresa' in form.fields:
            del form.fields['empresa']

        if form.is_valid():
            recebimento = form.save(commit=False)

            # Atribuir primeira empresa disponível
            primeira_empresa = Empresa.objects.first()
            if primeira_empresa:
                recebimento.empresa = primeira_empresa
            else:
                messages.error(request, "Nenhuma empresa cadastrada no sistema.")
                return redirect('dashboard')

            recebimento.usuario = request.user
            recebimento.save()
            messages.success(request, 'Recebimento registrado com sucesso!')
            return redirect('lista_recebimentos')
        else:
            # Mostrar erros de validação com nomes de campos traduzidos
            for field, errors in form.errors.items():
                if field in form.fields:
                    field_label = form.fields[field].label
                else:
                    field_label = field
                for error in errors:
                    messages.error(request, f"Campo '{field_label}': {error}")
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f"Erro: {error}")
    else:
        form = RecebimentoForm()
        # Remover campo empresa do formulário (será atribuído automaticamente)
        if 'empresa' in form.fields:
            del form.fields['empresa']

    contexto = {
        'form': form,
        'titulo': 'Registrar Novo Recebimento',
        'ultimos_recebimentos': Recebimento.objects.all().order_by('-data_recebimento')[:5]
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
    produtos = ProdutoFabricado.objects.select_related('item_associado').all()

    # Busca
    query = request.GET.get('q', '').strip()
    if query:
        produtos = produtos.filter(
            Q(nome__icontains=query) |
            Q(descricao__icontains=query)
        )

    # Ordenação
    ordenacao = request.GET.get('ordenar', 'nome')
    if ordenacao == 'nome':
        produtos = produtos.order_by('nome')
    elif ordenacao == 'data_desc':
        produtos = produtos.order_by('-id')  # Mais recentes primeiro
    elif ordenacao == 'data_asc':
        produtos = produtos.order_by('id')   # Mais antigos primeiro
    else:
        produtos = produtos.order_by('nome')  # Fallback

    contexto = {
        'produtos': produtos,
        'query': query,
        'ordenacao': ordenacao,
    }
    return render(request, 'core/lista_produtos.html', contexto)

@login_required
def detalhe_produto(request, pk):
    from datetime import datetime
    from django.db.models import Sum, Avg

    produto = get_object_or_404(ProdutoFabricado, pk=pk)
    componentes = produto.componente_set.all()

    # Lógica do Simulador
    form = ProducaoForm(request.GET or None)
    qtd_a_produzir = 1 # Valor padrão
    if form.is_valid():
        qtd_a_produzir = form.cleaned_data['quantidade_a_produzir']

    # Adicionando os cálculos a cada componente
    custo_total_estimado = 0
    todos_tem_estoque = True

    for componente in componentes:
        componente.total_necessario = componente.quantidade_necessaria * qtd_a_produzir
        componente.estoque_suficiente = componente.item_estoque.quantidade >= componente.total_necessario

        if not componente.estoque_suficiente:
            todos_tem_estoque = False

        # Calcular custo estimado usando o último preço do fornecedor
        ultimo_preco = componente.item_estoque.itemfornecedor_set.order_by('-data_cotacao').first()
        if ultimo_preco:
            componente.custo_unitario = ultimo_preco.valor_pago
            componente.custo_total = componente.custo_unitario * componente.total_necessario
            custo_total_estimado += componente.custo_total
        else:
            componente.custo_unitario = 0
            componente.custo_total = 0

    # Estatísticas do produto
    estoque_atual = produto.item_associado.quantidade
    data_criacao = produto.item_associado.data_criacao
    dias_desde_criacao = (datetime.now().date() - data_criacao.date()).days if data_criacao else 0

    # Média mensal aproximada (baseada no estoque atual e dias desde criação)
    if dias_desde_criacao > 0:
        media_mensal = (estoque_atual / dias_desde_criacao) * 30
    else:
        media_mensal = 0

    contexto = {
        'produto': produto,
        'componentes': componentes,
        'producao_form': form,
        'qtd_a_produzir': qtd_a_produzir,
        'custo_total_estimado': round(custo_total_estimado, 2),
        'custo_unitario_estimado': round(custo_total_estimado / qtd_a_produzir, 2) if qtd_a_produzir > 0 else 0,
        'todos_tem_estoque': todos_tem_estoque,
        # Estatísticas
        'estoque_atual': estoque_atual,
        'data_criacao': data_criacao,
        'media_mensal': round(media_mensal, 1),
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
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta

    # Pega todas as expedições da empresa do usuário
    expedicoes = Expedicao.objects.all()

    # Filtro por pesquisa (cliente ou nota fiscal)
    search_query = request.GET.get('search', '')
    if search_query:
        expedicoes = expedicoes.filter(
            Q(cliente__icontains=search_query) |
            Q(nota_fiscal__icontains=search_query)
        )

    # Ordenação
    order_by = request.GET.get('order_by', '-data_expedicao')
    valid_order_fields = ['-data_expedicao', 'data_expedicao', 'cliente', '-cliente', 'nota_fiscal', '-nota_fiscal']
    if order_by in valid_order_fields:
        expedicoes = expedicoes.order_by(order_by)

    # Estatísticas
    total_expedicoes = Expedicao.objects.count()

    # Total de itens expedidos (soma de todas as quantidades)
    total_itens_expedidos = ItemExpedido.objects.aggregate(
        total=Sum('quantidade')
    )['total'] or 0

    # Expedições dos últimos 30 dias
    data_limite = datetime.now() - timedelta(days=30)
    expedicoes_30_dias = Expedicao.objects.filter(data_expedicao__gte=data_limite).count()

    contexto = {
        'expedicoes': expedicoes,
        'total_expedicoes': total_expedicoes,
        'total_itens_expedidos': total_itens_expedidos,
        'expedicoes_30_dias': expedicoes_30_dias,
        'search_query': search_query,
        'order_by': order_by,
    }
    return render(request, 'core/lista_expedicoes.html', contexto)

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
        # Remover campo empresa do formulário (será atribuído automaticamente)
        if 'empresa' in form.fields:
            del form.fields['empresa']

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

            # Atribuir primeira empresa disponível
            primeira_empresa = Empresa.objects.first()
            if primeira_empresa:
                expedicao.empresa = primeira_empresa
            else:
                messages.error(request, "Nenhuma empresa cadastrada no sistema.")
                return redirect('dashboard')

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

# --- Views do Kanban ---

@login_required
def kanban_board(request):
    colunas = KanbanColumn.objects.all().order_by('ordem')
    tarefas_por_coluna = {str(coluna.id): list(coluna.tasks.all().order_by('ordem')) for coluna in colunas}
    historico = TaskQuantidadeFeita.objects.select_related('usuario', 'task').order_by('-data')[:30]
    contexto = {
        'colunas': colunas,
        'tarefas_por_coluna': tarefas_por_coluna,
        'historico': historico,
    }
    return render(request, 'core/kanban_board.html', contexto)

@login_required
def detalhe_tarefa(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    historico = task.historico.all()
    quantidades = task.quantidades_feitas.all()

    # Usuários que trabalharam neste card
    usuarios_trabalharam = User.objects.filter(
        Q(taskhistorico__task=task) | Q(taskquantidadefeita__task=task)
    ).distinct()

    contexto = {
        'task': task,
        'historico': historico,
        'quantidades': quantidades,
        'usuarios_trabalharam': usuarios_trabalharam,
    }
    return render(request, 'core/detalhe_tarefa.html', contexto)

@login_required
def metricas_kanban(request):
    from django.db.models import Count, Sum, Q

    # Cards finalizados por usuário - conta apenas cards ATUALMENTE finalizados
    # Para cada usuário, busca o último histórico de finalização/reabertura de cada card
    # e conta apenas se o último registro for de finalização

    # Cálculo proporcional: cada usuário recebe crédito fracionado baseado em sua contribuição
    # Exemplo: Card de 100 unidades - User A produziu 60 (0.6 cards) + User B produziu 40 (0.4 cards)

    from decimal import Decimal

    # Primeiro, pegamos todos os usuários que produziram algo
    usuarios = User.objects.annotate(
        total_quantidade_produzida=Sum('taskquantidadefeita__quantidade')
    ).filter(total_quantidade_produzida__gt=0)

    # Para cada usuário, calculamos sua contribuição proporcional em cards finalizados
    cards_por_usuario = []
    for user in usuarios:
        # Buscar todos os cards finalizados atualmente
        tasks_finalizadas = Task.objects.filter(finalizado=True)

        cards_finalizados_proporcional = Decimal('0.0')

        # Para cada card finalizado, calcular a contribuição proporcional do usuário
        for task in tasks_finalizadas:
            # Total produzido neste card
            total_produzido_card = task.quantidade_produzida

            if total_produzido_card > 0:
                # Quantidade que este usuário produziu neste card
                quantidade_usuario = TaskQuantidadeFeita.objects.filter(
                    task=task,
                    usuario=user
                ).aggregate(total=Sum('quantidade'))['total'] or 0

                # Calcular proporção (0.0 a 1.0)
                if quantidade_usuario > 0:
                    proporcao = Decimal(quantidade_usuario) / Decimal(total_produzido_card)
                    cards_finalizados_proporcional += proporcao

        if cards_finalizados_proporcional > 0 or user.total_quantidade_produzida:
            media_por_card = (user.total_quantidade_produzida / float(cards_finalizados_proporcional)) if cards_finalizados_proporcional > 0 else 0
            cards_por_usuario.append({
                'user': user,
                'total_finalizados': float(cards_finalizados_proporcional),
                'total_quantidade_produzida': user.total_quantidade_produzida or 0,
                'media_por_card': media_por_card
            })

    # Ordenar por total_finalizados (decrescente)
    cards_por_usuario = sorted(cards_por_usuario, key=lambda x: x['total_finalizados'], reverse=True)

    # Total de cards finalizados ATUALMENTE
    total_cards_finalizados = Task.objects.filter(finalizado=True).count()

    # Total de cards em andamento
    total_cards_andamento = Task.objects.filter(em_andamento=True, finalizado=False).count()

    # Total de quantidade produzida
    total_produzido = TaskQuantidadeFeita.objects.aggregate(total=Sum('quantidade'))['total'] or 0

    contexto = {
        'cards_por_usuario': cards_por_usuario,
        'total_cards_finalizados': total_cards_finalizados,
        'total_cards_andamento': total_cards_andamento,
        'total_produzido': total_produzido,
    }
    return render(request, 'core/metricas_kanban.html', contexto)

@login_required
def criar_coluna(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cor = request.POST.get('cor', '#f3f4f6')
        ordem = KanbanColumn.objects.count()
        coluna = KanbanColumn.objects.create(nome=nome, cor=cor, ordem=ordem)
        return redirect('kanban_board')
    return render(request, 'core/form_coluna.html')

@login_required
def editar_coluna(request, coluna_id):
    coluna = get_object_or_404(KanbanColumn, id=coluna_id)
    if request.method == 'POST':
        coluna.nome = request.POST.get('nome')
        coluna.cor = request.POST.get('cor', coluna.cor)

        # Processar mudança de posição
        nova_posicao = request.POST.get('posicao')
        if nova_posicao is not None:
            nova_posicao = int(nova_posicao)
            posicao_atual = coluna.ordem

            if nova_posicao != posicao_atual:
                # Reordenar todas as colunas
                colunas = list(KanbanColumn.objects.all().order_by('ordem'))

                # Remove a coluna atual da lista
                colunas.pop(posicao_atual)

                # Insere na nova posição
                colunas.insert(nova_posicao, coluna)

                # Atualiza a ordem de todas as colunas
                for idx, col in enumerate(colunas):
                    col.ordem = idx
                    col.save(update_fields=['ordem'])

        coluna.save()
        return redirect('kanban_board')

    # Preparar dados para o template
    total_colunas = KanbanColumn.objects.count()
    context = {
        'coluna': coluna,
        'range_posicoes': range(total_colunas),
        'posicao_atual': coluna.ordem,
        'total_colunas': total_colunas
    }
    return render(request, 'core/form_coluna.html', context)

@login_required
def excluir_coluna(request, coluna_id):
    coluna = get_object_or_404(KanbanColumn, id=coluna_id)
    if request.method == 'POST':
        coluna.delete()
        return redirect('kanban_board')
    return render(request, 'core/confirmar_exclusao.html', {'obj': coluna, 'tipo': 'coluna'})

@login_required
def criar_tarefa(request, coluna_id=None):
    if request.method == 'POST':
        coluna = get_object_or_404(KanbanColumn, id=request.POST.get('coluna_id', coluna_id))
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao', '')
        quantidade_meta = int(request.POST.get('quantidade', 0))
        ordem = coluna.tasks.count()
        task = Task.objects.create(coluna=coluna, titulo=titulo, descricao=descricao, quantidade_meta=quantidade_meta, ordem=ordem)
        responsaveis_ids = request.POST.getlist('responsaveis')
        if responsaveis_ids:
            task.responsaveis.set(responsaveis_ids)

        # Registra histórico
        TaskHistorico.objects.create(
            task=task,
            usuario=request.user,
            tipo_acao='criado',
            descricao=f'Card criado na coluna "{coluna.nome}" com meta de {quantidade_meta} unidades'
        )
        return redirect('kanban_board')
    colunas = KanbanColumn.objects.all()
    users = User.objects.all()
    return render(request, 'core/form_tarefa.html', {'colunas': colunas, 'users': users, 'coluna_id': coluna_id})

@login_required
def editar_tarefa(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        old_titulo = task.titulo
        old_responsaveis = set(task.responsaveis.all())

        task.titulo = request.POST.get('titulo')
        task.descricao = request.POST.get('descricao', '')
        task.quantidade_meta = int(request.POST.get('quantidade', 0))
        task.coluna_id = request.POST.get('coluna_id', task.coluna_id)
        responsaveis_ids = request.POST.getlist('responsaveis')
        task.responsaveis.set(responsaveis_ids)
        task.save()

        new_responsaveis = set(task.responsaveis.all())

        # Registra histórico de edição
        if old_titulo != task.titulo:
            TaskHistorico.objects.create(
                task=task,
                usuario=request.user,
                tipo_acao='editado',
                descricao=f'Título alterado de "{old_titulo}" para "{task.titulo}"'
            )

        # Verifica mudanças nos responsáveis
        adicionados = new_responsaveis - old_responsaveis
        removidos = old_responsaveis - new_responsaveis

        for user in adicionados:
            TaskHistorico.objects.create(
                task=task,
                usuario=request.user,
                tipo_acao='responsavel_adicionado',
                descricao=f'{user.get_full_name() or user.username} adicionado como responsável'
            )

        for user in removidos:
            TaskHistorico.objects.create(
                task=task,
                usuario=request.user,
                tipo_acao='responsavel_removido',
                descricao=f'{user.get_full_name() or user.username} removido dos responsáveis'
            )

        return redirect('kanban_board')
    colunas = KanbanColumn.objects.all()
    users = User.objects.all()
    return render(request, 'core/form_tarefa.html', {'task': task, 'colunas': colunas, 'users': users})

@login_required
def excluir_tarefa(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('kanban_board')
    return render(request, 'core/confirmar_exclusao.html', {'obj': task, 'tipo': 'tarefa'})

@login_required
@require_POST
def mover_tarefa(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        nova_coluna_id = request.POST.get('nova_coluna_id')
        nova_ordem = int(request.POST.get('nova_ordem', 0))

        if nova_coluna_id:
            coluna_antiga = task.coluna
            nova_coluna = get_object_or_404(KanbanColumn, id=nova_coluna_id)

            if coluna_antiga.id != nova_coluna.id:
                task.coluna = nova_coluna
                # Registra histórico
                TaskHistorico.objects.create(
                    task=task,
                    usuario=request.user,
                    tipo_acao='movido',
                    descricao=f'Movido de "{coluna_antiga.nome}" para "{nova_coluna.nome}"'
                )

        task.ordem = nova_ordem
        task.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def mover_coluna(request, coluna_id):
    coluna = get_object_or_404(KanbanColumn, id=coluna_id)
    nova_ordem = int(request.POST.get('nova_ordem', 0))
    coluna.ordem = nova_ordem
    coluna.save()
    return JsonResponse({'success': True})

@login_required
@require_POST
def marcar_andamento(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.em_andamento = True
    task.save()

    # Registra histórico
    TaskHistorico.objects.create(
        task=task,
        usuario=request.user,
        tipo_acao='iniciado',
        descricao=f'Card iniciado por {request.user.get_full_name() or request.user.username}'
    )
    return redirect('kanban_board')

@login_required
@require_POST
def finalizar(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.em_andamento = False
    task.finalizado = True
    task.data_finalizacao = timezone.now()
    task.save()

    # Registra histórico
    TaskHistorico.objects.create(
        task=task,
        usuario=request.user,
        tipo_acao='finalizado',
        descricao=f'Card finalizado por {request.user.get_full_name() or request.user.username}'
    )
    return redirect('kanban_board')

@login_required
@require_POST
def desfinalizar(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.finalizado = False
    task.data_finalizacao = None
    task.save()

    # Registra histórico
    TaskHistorico.objects.create(
        task=task,
        usuario=request.user,
        tipo_acao='editado',
        descricao=f'Card desfinalizadopor {request.user.get_full_name() or request.user.username}'
    )
    return redirect('kanban_board')

@login_required
@require_POST
def registrar_quantidade(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    quantidade = int(request.POST.get('quantidade', 0))
    if quantidade > 0:
        TaskQuantidadeFeita.objects.create(task=task, usuario=request.user, quantidade=quantidade)

        # Registra histórico
        TaskHistorico.objects.create(
            task=task,
            usuario=request.user,
            tipo_acao='quantidade_adicionada',
            descricao=f'{request.user.get_full_name() or request.user.username} produziu {quantidade} unidade(s). Total: {task.quantidade_produzida}/{task.quantidade_meta}'
        )
    return redirect('kanban_board')

@login_required
@require_POST
def editar_quantidade_feita(request, quantidade_id):
    """Edita uma quantidade feita existente"""
    quantidade_obj = get_object_or_404(TaskQuantidadeFeita, id=quantidade_id)
    task = quantidade_obj.task
    quantidade_antiga = quantidade_obj.quantidade

    nova_quantidade = int(request.POST.get('quantidade', 0))
    if nova_quantidade > 0:
        quantidade_obj.quantidade = nova_quantidade
        quantidade_obj.save()

        # Registra histórico
        TaskHistorico.objects.create(
            task=task,
            usuario=request.user,
            tipo_acao='quantidade_editada',
            descricao=f'{request.user.get_full_name() or request.user.username} editou quantidade de {quantidade_antiga} para {nova_quantidade} unidades. Total: {task.quantidade_produzida}/{task.quantidade_meta}'
        )
        messages.success(request, f'Quantidade atualizada de {quantidade_antiga} para {nova_quantidade} unidades!')
    else:
        messages.error(request, 'Quantidade deve ser maior que zero.')

    return redirect('kanban_board')

@login_required
@require_POST
def excluir_quantidade_feita(request, quantidade_id):
    """Exclui uma quantidade feita"""
    quantidade_obj = get_object_or_404(TaskQuantidadeFeita, id=quantidade_id)
    task = quantidade_obj.task
    quantidade_valor = quantidade_obj.quantidade
    usuario_nome = quantidade_obj.usuario.get_full_name() or quantidade_obj.usuario.username if quantidade_obj.usuario else 'Usuário desconhecido'

    # Registra histórico antes de excluir
    TaskHistorico.objects.create(
        task=task,
        usuario=request.user,
        tipo_acao='quantidade_removida',
        descricao=f'{request.user.get_full_name() or request.user.username} removeu registro de {quantidade_valor} unidades (feito por {usuario_nome}). Total atual: {task.quantidade_produzida - quantidade_valor}/{task.quantidade_meta}'
    )

    quantidade_obj.delete()
    messages.success(request, f'Registro de {quantidade_valor} unidades removido com sucesso!')

    return redirect('kanban_board')

# --- Views de Controle de Ponto ---

@login_required
def controle_ponto(request):
    """View principal do controle de ponto"""
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count
    import calendar

    # Verifica se é superusuário ou o próprio usuário
    usuario_id = request.GET.get('usuario_id')
    if usuario_id and request.user.is_superuser:
        usuario = get_object_or_404(User, id=usuario_id)
    else:
        usuario = request.user

    # Criar jornada se não existir
    jornada, created = JornadaTrabalho.objects.get_or_create(
        usuario=usuario,
        defaults={'horas_diarias': 9.0, 'horas_sexta': 8.0, 'intervalo_almoco': 1.0}
    )

    # Dados do mês atual (usando período personalizado do funcionário)
    now = datetime.now()
    dia_inicio = jornada.dia_inicio_mes
    dia_fim = jornada.dia_fim_mes

    # Calcular primeiro e último dia do período personalizado
    if dia_inicio == 1 and dia_fim == 0:
        # Período padrão: do dia 1 ao último dia do mês
        primeiro_dia = datetime(now.year, now.month, 1)
        ultimo_dia = datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1], 23, 59, 59)
    else:
        # Período personalizado
        if dia_fim == 0:
            # 0 significa último dia do mês
            dia_fim = calendar.monthrange(now.year, now.month)[1]

        # Se estamos depois do dia de início, o período é do dia_inicio deste mês até dia_fim do próximo mês
        # Se estamos antes do dia de início, o período é do dia_inicio do mês passado até dia_fim deste mês
        if now.day >= dia_inicio:
            # Período atual: dia_inicio deste mês até dia_fim do próximo mês (ou mesmo mês se dia_fim > dia_inicio)
            primeiro_dia = datetime(now.year, now.month, dia_inicio, 0, 0, 0)

            if dia_fim >= dia_inicio:
                # Período termina no mesmo mês
                ultimo_dia = datetime(now.year, now.month, dia_fim, 23, 59, 59)
            else:
                # Período termina no próximo mês
                if now.month == 12:
                    proximo_mes = 1
                    proximo_ano = now.year + 1
                else:
                    proximo_mes = now.month + 1
                    proximo_ano = now.year
                ultimo_dia = datetime(proximo_ano, proximo_mes, dia_fim, 23, 59, 59)
        else:
            # Período anterior: dia_inicio do mês passado até dia_fim deste mês
            if now.month == 1:
                mes_anterior = 12
                ano_anterior = now.year - 1
            else:
                mes_anterior = now.month - 1
                ano_anterior = now.year

            primeiro_dia = datetime(ano_anterior, mes_anterior, dia_inicio, 0, 0, 0)
            ultimo_dia = datetime(now.year, now.month, dia_fim, 23, 59, 59)

    # Registros de ponto do mês
    pontos_mes = RegistroPonto.objects.filter(
        usuario=usuario,
        data_hora__gte=primeiro_dia,
        data_hora__lte=ultimo_dia
    ).order_by('-data_hora')

    # Calcular horas trabalhadas no mês
    horas_trabalhadas = 0
    dias_trabalhados = {}

    for ponto in pontos_mes:
        dia = ponto.data_hora.date()
        if dia not in dias_trabalhados:
            dias_trabalhados[dia] = {'entrada': None, 'saida': None, 'inicio_almoco': None, 'fim_almoco': None}

        if ponto.tipo == 'entrada':
            dias_trabalhados[dia]['entrada'] = ponto.data_hora
        elif ponto.tipo == 'saida':
            dias_trabalhados[dia]['saida'] = ponto.data_hora
        elif ponto.tipo == 'inicio_almoco':
            dias_trabalhados[dia]['inicio_almoco'] = ponto.data_hora
        elif ponto.tipo == 'fim_almoco':
            dias_trabalhados[dia]['fim_almoco'] = ponto.data_hora

    # Calcular horas de cada dia
    for dia, registros in dias_trabalhados.items():
        if registros['entrada'] and registros['saida']:
            delta = registros['saida'] - registros['entrada']
            horas_brutas = delta.total_seconds() / 3600

            # Descontar intervalo de almoço se registrado
            if registros['inicio_almoco'] and registros['fim_almoco']:
                intervalo = registros['fim_almoco'] - registros['inicio_almoco']
                horas_brutas -= intervalo.total_seconds() / 3600

            horas_trabalhadas += horas_brutas

    # Calcular horas abonadas separadamente
    abonos_periodo = AbonoDia.objects.filter(
        usuario=usuario,
        data__gte=primeiro_dia.date(),
        data__lte=ultimo_dia.date()
    )
    horas_abonadas = sum(float(abono.horas_abonadas) for abono in abonos_periodo)

    # Calcular dias de falta (dias úteis sem ponto e sem abono, até hoje)
    dias_falta = 0
    dia_atual = primeiro_dia.date()
    hoje = now.date()
    dias_semana_trabalho = [int(d) for d in jornada.dias_semana.split(',')]

    # Calcular apenas até hoje, não até o fim do período
    data_limite = min(ultimo_dia.date(), hoje)

    while dia_atual <= data_limite:
        # Verifica se é dia de trabalho (considerando dias_semana configurados)
        if dia_atual.weekday() in dias_semana_trabalho:
            # Verifica se não tem registro de ponto neste dia
            tem_ponto = RegistroPonto.objects.filter(
                usuario=usuario,
                data_hora__date=dia_atual
            ).exists()

            # Verifica se não tem abono neste dia
            tem_abono = AbonoDia.objects.filter(
                usuario=usuario,
                data=dia_atual
            ).exists()

            # Se não tem ponto e não tem abono, é falta
            if not tem_ponto and not tem_abono:
                dias_falta += 1

        dia_atual += timedelta(days=1)

    # Último ponto do dia
    ultimo_ponto_hoje = RegistroPonto.objects.filter(
        usuario=usuario,
        data_hora__date=hoje
    ).order_by('-data_hora').first()

    # Horas esperadas no mês
    horas_esperadas = jornada.horas_mensais

    # Saldo de horas (inclui horas abonadas no cálculo)
    saldo_horas = (horas_trabalhadas + horas_abonadas) - horas_esperadas

    # Últimos 30 dias para gráfico com cores baseadas em horas trabalhadas
    trinta_dias_atras = now - timedelta(days=30)
    presenca_ultimos_30 = []

    # Obter dias de trabalho configurados na jornada
    dias_semana_trabalho = [int(d) for d in jornada.dias_semana.split(',')]

    for i in range(30):
        dia = (now - timedelta(days=29-i)).date()

        # Buscar pontos do dia
        pontos_dia = RegistroPonto.objects.filter(
            usuario=usuario,
            data_hora__date=dia
        ).order_by('data_hora')

        # Calcular horas trabalhadas no dia
        horas_dia = 0
        registros_dia = {'entrada': None, 'saida': None, 'inicio_almoco': None, 'fim_almoco': None}

        for ponto in pontos_dia:
            if ponto.tipo == 'entrada':
                registros_dia['entrada'] = ponto.data_hora
            elif ponto.tipo == 'saida':
                registros_dia['saida'] = ponto.data_hora
            elif ponto.tipo == 'inicio_almoco':
                registros_dia['inicio_almoco'] = ponto.data_hora
            elif ponto.tipo == 'fim_almoco':
                registros_dia['fim_almoco'] = ponto.data_hora

        # Verificar se o dia foi abonado
        abono_dia = AbonoDia.objects.filter(usuario=usuario, data=dia).first()

        # Calcular horas líquidas
        if registros_dia['entrada'] and registros_dia['saida']:
            delta = registros_dia['saida'] - registros_dia['entrada']
            horas_dia = delta.total_seconds() / 3600

            # Descontar intervalo de almoço
            if registros_dia['inicio_almoco'] and registros_dia['fim_almoco']:
                intervalo = registros_dia['fim_almoco'] - registros_dia['inicio_almoco']
                horas_dia -= intervalo.total_seconds() / 3600

        # Definir cor baseada no percentual das horas esperadas (considera sexta diferente)
        horas_esperadas_dia = jornada.horas_esperadas_dia(dia)

        # Verificar se é dia útil (está nos dias de trabalho configurados)
        dia_util = dia.weekday() in dias_semana_trabalho

        # Se o dia foi abonado, usar cor amarela
        if abono_dia:
            cor = 'bg-yellow-500/50'  # Amarelo com 50% transparência: dia abonado
            percentual = 100  # Considerar como 100% por ser abonado
            horas_dia = float(abono_dia.horas_abonadas)  # Usar horas abonadas
        elif not dia_util:
            cor = 'bg-gray-300'  # Cinza: dia não útil (fim de semana/feriado)
            percentual = 0
        elif horas_dia == 0:
            cor = 'bg-red-500/50'  # Vermelho com 50% transparência: falta (dia útil sem registro)
            percentual = 0
        else:
            percentual = (horas_dia / horas_esperadas_dia) * 100
            if percentual >= 100:
                cor = 'bg-green-500'  # Verde chamativo: 100%+
            elif percentual >= 75:
                cor = 'bg-green-500/75'  # Verde com 25% transparência: 75-99%
            elif percentual >= 50:
                cor = 'bg-green-500/55'  # Verde com 45% transparência: 50-74%
            elif percentual >= 25:
                cor = 'bg-green-500/35'  # Verde com 65% transparência: 25-49%
            else:
                cor = 'bg-green-500/15'  # Verde com 85% transparência: 1-24%

        presenca_ultimos_30.append({
            'dia': dia.strftime('%d/%m'),
            'presente': horas_dia > 0 or abono_dia is not None,
            'horas': round(horas_dia, 2),
            'cor': cor,
            'percentual': round(percentual, 0),
            'abonado': abono_dia is not None,
            'tipo_abono': abono_dia.get_tipo_abono_display() if abono_dia else None,
            'dia_util': dia_util
        })

    # Lista de usuários (apenas para superusuário)
    usuarios = User.objects.filter(is_active=True) if request.user.is_superuser else []

    # Abonos do mês (para superusuário)
    abonos_mes = AbonoDia.objects.filter(
        data__gte=primeiro_dia.date(),
        data__lte=ultimo_dia.date()
    ).order_by('-data') if request.user.is_superuser else []

    contexto = {
        'usuario_selecionado': usuario,
        'jornada': jornada,
        'pontos_mes': pontos_mes[:10],  # Últimos 10 registros
        'horas_trabalhadas': round(horas_trabalhadas, 2),
        'horas_abonadas': round(horas_abonadas, 2),
        'horas_esperadas': round(horas_esperadas, 2),
        'saldo_horas': round(saldo_horas, 2),
        'dias_trabalhados': len([d for d, r in dias_trabalhados.items() if r['entrada'] and r['saida']]),
        'dias_falta': dias_falta,
        'ultimo_ponto_hoje': ultimo_ponto_hoje,
        'presenca_ultimos_30': presenca_ultimos_30,
        'usuarios': usuarios,
        'abonos_mes': abonos_mes,
        'primeiro_dia': primeiro_dia,
        'ultimo_dia': ultimo_dia,
    }

    return render(request, 'core/controle_ponto.html', contexto)

@login_required
@require_POST
def bater_ponto(request):
    """Registra entrada, saída ou almoço"""
    tipo = request.POST.get('tipo')
    observacao = request.POST.get('observacao', '')

    if tipo not in ['entrada', 'saida', 'inicio_almoco', 'fim_almoco']:
        messages.error(request, 'Tipo de ponto inválido.')
        return redirect('controle_ponto')

    # Verifica o último ponto do dia
    hoje = timezone.now().date()
    ultimo_ponto = RegistroPonto.objects.filter(
        usuario=request.user,
        data_hora__date=hoje
    ).order_by('-data_hora').first()

    # Validações
    if tipo == 'entrada' and ultimo_ponto and ultimo_ponto.tipo in ['entrada', 'inicio_almoco']:
        messages.error(request, 'Você já registrou uma entrada. Registre a saída ou fim do almoço primeiro.')
        return redirect('controle_ponto')

    if tipo == 'inicio_almoco' and (not ultimo_ponto or ultimo_ponto.tipo != 'entrada'):
        messages.error(request, 'Você precisa registrar a entrada antes de iniciar o almoço.')
        return redirect('controle_ponto')

    if tipo == 'fim_almoco' and (not ultimo_ponto or ultimo_ponto.tipo != 'inicio_almoco'):
        messages.error(request, 'Você precisa registrar o início do almoço primeiro.')
        return redirect('controle_ponto')

    if tipo == 'saida' and (not ultimo_ponto or ultimo_ponto.tipo in ['saida', 'inicio_almoco']):
        messages.error(request, 'Você precisa registrar entrada/fim de almoço antes da saída.')
        return redirect('controle_ponto')

    # Registra o ponto
    RegistroPonto.objects.create(
        usuario=request.user,
        tipo=tipo,
        observacao=observacao
    )

    # Mensagem de sucesso
    mensagens_tipo = {
        'entrada': 'Entrada',
        'saida': 'Saída',
        'inicio_almoco': 'Início do Almoço',
        'fim_almoco': 'Fim do Almoço'
    }
    tipo_texto = mensagens_tipo.get(tipo, tipo)
    messages.success(request, f'{tipo_texto} registrado com sucesso às {timezone.now().strftime("%H:%M")}!')

    return redirect('controle_ponto')

@login_required
def abonar_dia(request):
    """Permite superuser abonar dia completo de um funcionário"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para abonar dias.')
        return redirect('controle_ponto')

    if request.method == 'POST':
        from datetime import datetime
        usuario_id = request.POST.get('usuario_id')
        data_str = request.POST.get('data')
        tipo_abono = request.POST.get('tipo_abono')
        motivo = request.POST.get('motivo')
        horas_abonadas = request.POST.get('horas_abonadas', 8.0)

        try:
            usuario = User.objects.get(pk=usuario_id)
            data = datetime.strptime(data_str, '%Y-%m-%d').date()

            # Verificar se já existe abono para este dia
            if AbonoDia.objects.filter(usuario=usuario, data=data).exists():
                messages.warning(request, f'Já existe um abono para {usuario.username} no dia {data.strftime("%d/%m/%Y")}.')
                return redirect('controle_ponto')

            # Criar abono
            AbonoDia.objects.create(
                usuario=usuario,
                data=data,
                tipo_abono=tipo_abono,
                motivo=motivo,
                horas_abonadas=horas_abonadas,
                abonado_por=request.user
            )

            messages.success(request, f'Dia {data.strftime("%d/%m/%Y")} abonado com sucesso para {usuario.username}!')
            return redirect('controle_ponto')

        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
        except ValueError:
            messages.error(request, 'Data inválida.')
        except Exception as e:
            messages.error(request, f'Erro ao abonar dia: {str(e)}')

    return redirect('controle_ponto')

@superuser_required
def remover_abono_dia(request, abono_id):
    """Permite superuser remover um abono de dia"""

    try:
        abono = AbonoDia.objects.get(pk=abono_id)
        usuario_nome = abono.usuario.username
        data = abono.data.strftime("%d/%m/%Y")
        abono.delete()
        messages.success(request, f'Abono do dia {data} de {usuario_nome} foi removido.')
    except AbonoDia.DoesNotExist:
        messages.error(request, 'Abono não encontrado.')

    return redirect('controle_ponto')

@superuser_required
def configurar_periodo_mes(request):
    """Permite superuser configurar período de mês personalizado para funcionário"""

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        dia_inicio = request.POST.get('dia_inicio_mes')
        dia_fim = request.POST.get('dia_fim_mes')

        try:
            usuario = User.objects.get(pk=usuario_id)
            jornada, created = JornadaTrabalho.objects.get_or_create(usuario=usuario)

            # Validar dias (1-31 ou 0 para último dia)
            dia_inicio = int(dia_inicio)
            dia_fim = int(dia_fim)

            if dia_inicio < 1 or dia_inicio > 31:
                messages.error(request, 'Dia de início deve ser entre 1 e 31.')
                return redirect('controle_ponto')

            if dia_fim < 0 or dia_fim > 31:
                messages.error(request, 'Dia de fim deve ser entre 0 (último dia) e 31.')
                return redirect('controle_ponto')

            # Atualizar jornada
            jornada.dia_inicio_mes = dia_inicio
            jornada.dia_fim_mes = dia_fim
            jornada.save()

            if dia_fim == 0:
                periodo_info = f"dia {dia_inicio} ao último dia do mês"
            else:
                periodo_info = f"dia {dia_inicio} ao dia {dia_fim}"

            messages.success(request, f'Período personalizado configurado para {usuario.username}: {periodo_info}')
            return redirect('controle_ponto')

        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
        except ValueError:
            messages.error(request, 'Valores inválidos para os dias.')
        except Exception as e:
            messages.error(request, f'Erro ao configurar período: {str(e)}')

    return redirect('controle_ponto')

# === VIEWS DE CLIENTES ===

@login_required
def lista_clientes(request):
    from django.db.models import Count

    # SEGURANÇA: Filtrar apenas clientes da empresa do usuário
    clientes = Cliente.objects.all()
    clientes = filter_by_empresa(clientes, request.user)
    clientes = clientes.annotate(total_produtos=Count('produtos_fornecidos')).order_by('nome')

    # Filtros
    query = request.GET.get('q', '')
    mercado = request.GET.get('mercado', '')

    if query:
        clientes = clientes.filter(Q(nome__icontains=query) | Q(email__icontains=query))
    if mercado:
        clientes = clientes.filter(mercado=mercado)

    contexto = {
        'clientes': clientes,
        'query': query,
        'mercado_filtro': mercado,
        'total_clientes': clientes.count(),
    }
    return render(request, 'core/lista_clientes.html', contexto)

@login_required
def adicionar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            primeira_empresa = Empresa.objects.first()
            if primeira_empresa:
                cliente.empresa = primeira_empresa
            cliente.save()
            form.save_m2m()
            messages.success(request, f'Cliente "{cliente.nome}" cadastrado com sucesso!')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()

    return render(request, 'core/form_cliente.html', {'form': form, 'titulo': 'Adicionar Cliente'})

@login_required
def editar_cliente(request, pk):
    # SEGURANÇA: Garantir que o cliente pertence à empresa do usuário
    empresas = get_user_empresa(request.user)
    cliente = get_object_or_404(Cliente, pk=pk, empresa__in=empresas)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente "{cliente.nome}" atualizado com sucesso!')
            return redirect('detalhe_cliente', pk=pk)
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'core/form_cliente.html', {'form': form, 'titulo': f'Editar {cliente.nome}', 'cliente': cliente})

@login_required
def detalhe_cliente(request, pk):
    # SEGURANÇA: Garantir que o cliente pertence à empresa do usuário
    empresas = get_user_empresa(request.user)
    cliente = get_object_or_404(Cliente, pk=pk, empresa__in=empresas)
    return render(request, 'core/detalhe_cliente.html', {'cliente': cliente})

@login_required
def excluir_cliente(request, pk):
    # SEGURANÇA: Garantir que o cliente pertence à empresa do usuário
    empresas = get_user_empresa(request.user)
    cliente = get_object_or_404(Cliente, pk=pk, empresa__in=empresas)

    if request.method == 'POST':
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'Cliente "{nome}" excluído com sucesso!')
        return redirect('lista_clientes')
    return redirect('detalhe_cliente', pk=pk)

# === VIEWS DE FORNECEDORES ===

@login_required
def lista_fornecedores(request):
    # SEGURANÇA: Filtrar apenas fornecedores da empresa do usuário
    fornecedores = Fornecedor.objects.all()
    fornecedores = filter_by_empresa(fornecedores, request.user)
    fornecedores = fornecedores.order_by('nome')

    # Filtros
    query = request.GET.get('q', '')
    mercado = request.GET.get('mercado', '')

    if query:
        fornecedores = fornecedores.filter(Q(nome__icontains=query) | Q(email__icontains=query))
    if mercado:
        fornecedores = fornecedores.filter(mercado=mercado)

    contexto = {
        'fornecedores': fornecedores,
        'query': query,
        'mercado_filtro': mercado,
        'total_fornecedores': fornecedores.count(),
    }
    return render(request, 'core/lista_fornecedores.html', contexto)

@login_required
def adicionar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            fornecedor = form.save(commit=False)
            primeira_empresa = Empresa.objects.first()
            if primeira_empresa:
                fornecedor.empresa = primeira_empresa
            fornecedor.save()
            messages.success(request, f'Fornecedor "{fornecedor.nome}" cadastrado com sucesso!')
            return redirect('lista_fornecedores')
    else:
        form = FornecedorForm()

    return render(request, 'core/form_fornecedor.html', {'form': form, 'titulo': 'Adicionar Fornecedor'})

@login_required
def editar_fornecedor(request, pk):
    # SEGURANÇA: Garantir que o fornecedor pertence à empresa do usuário
    empresas = get_user_empresa(request.user)
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa__in=empresas)

    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fornecedor "{fornecedor.nome}" atualizado com sucesso!')
            return redirect('detalhe_fornecedor', pk=pk)
    else:
        form = FornecedorForm(instance=fornecedor)

    return render(request, 'core/form_fornecedor.html', {'form': form, 'titulo': f'Editar {fornecedor.nome}', 'fornecedor': fornecedor})

@login_required
def detalhe_fornecedor(request, pk):
    # SEGURANÇA: Garantir que o fornecedor pertence à empresa do usuário
    empresas = get_user_empresa(request.user)
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa__in=empresas)
    return render(request, 'core/detalhe_fornecedor.html', {'fornecedor': fornecedor})

@login_required
def excluir_fornecedor(request, pk):
    # SEGURANÇA: Garantir que o fornecedor pertence à empresa do usuário
    empresas = get_user_empresa(request.user)
    fornecedor = get_object_or_404(Fornecedor, pk=pk, empresa__in=empresas)

    if request.method == 'POST':
        nome = fornecedor.nome
        fornecedor.delete()
        messages.success(request, f'Fornecedor "{nome}" excluído com sucesso!')
        return redirect('lista_fornecedores')
    return redirect('detalhe_fornecedor', pk=pk)