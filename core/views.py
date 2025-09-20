# core/views.py
from django.shortcuts import render
# Importe o modelo que queremos usar
from .models import ItemEstoque

# Esta é a nossa view. Ela recebe uma 'request' do navegador.
def lista_estoque(request):
    # 1. A Lógica: Buscamos TODOS os objetos do modelo ItemEstoque.
    #    O ORM do Django torna isso incrivelmente simples.
    #    'order_by('nome')' organiza os itens em ordem alfabética.
    itens = ItemEstoque.objects.all().order_by('nome')

    # 2. O Contexto: Criamos um "dicionário de contexto".
    #    É assim que passamos dados da view para o template.
    #    A chave 'itens' será o nome da variável no template.
    contexto = {
        'itens': itens
    }

    # 3. A Resposta: Renderizamos o template, passando a request e o contexto.
    #    O Django vai procurar por 'core/lista_estoque.html'.
    return render(request, 'core/lista_estoque.html', contexto)