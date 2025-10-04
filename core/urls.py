from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # --- Rotas de Estoque ---
    path('estoque/', views.lista_estoque, name='lista_estoque'),
    path('estoque/historico/', views.historico_geral_estoque, name='historico_geral_estoque'),
    path('estoque/adicionar/', views.adicionar_item, name='adicionar_item'),
    path('estoque/<int:pk>/gerenciar/', views.gerenciar_item, name='gerenciar_item'),
    path('estoque/<int:pk>/historico/', views.historico_completo_item, name='historico_completo_item'),
    path('estoque/<int:pk>/retirar/', views.retirar_item, name='retirar_item'),
    path('estoque/<int:pk>/adicionar-estoque/', views.adicionar_estoque, name='adicionar_estoque'),
    path('estoque/<int:pk>/duplicar/', views.duplicar_item, name='duplicar_item'),
    path('estoque/<int:pk>/excluir/', views.excluir_item, name='excluir_item'),
    
    # --- Rotas de Recebimento ---
    path('recebimento/', views.lista_recebimentos, name='lista_recebimentos'),
    path('recebimento/registrar/', views.registrar_recebimento, name='registrar_recebimento'),
    path('recebimento/<int:pk>/', views.detalhe_recebimento, name='detalhe_recebimento'),
    path('recebimento/<int:pk>/editar/', views.editar_recebimento, name='editar_recebimento'),
    path('recebimento/<int:pk>/excluir/', views.excluir_recebimento, name='excluir_recebimento'),

    # --- Rotas de Produto ---
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('produtos/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('produtos/<int:pk>/', views.detalhe_produto, name='detalhe_produto'),
    path('produtos/<int:pk>/editar/', views.editar_produto, name='editar_produto'),
    path('produtos/<int:pk>/excluir/', views.excluir_produto, name='excluir_produto'),

    # --- Rotas de Expedição ---
    path('expedicao/', views.lista_expedicoes, name='lista_expedicoes'),
    path('expedicao/registrar/', views.registrar_expedicao, name='registrar_expedicao'),
    path('expedicao/<int:pk>/', views.detalhe_expedicao, name='detalhe_expedicao'),
    path('expedicao/<int:pk>/editar/', views.editar_expedicao, name='editar_expedicao'),
    path('expedicao/<int:pk>/excluir/', views.excluir_expedicao, name='excluir_expedicao'),

    # --- Rotas Kanban ---
    path('kanban/', views.kanban_board, name='kanban_board'),
    path('kanban/metricas/', views.metricas_kanban, name='metricas_kanban'),
    path('kanban/coluna/nova/', views.criar_coluna, name='criar_coluna'),
    path('kanban/coluna/<int:coluna_id>/editar/', views.editar_coluna, name='editar_coluna'),
    path('kanban/coluna/<int:coluna_id>/excluir/', views.excluir_coluna, name='excluir_coluna'),
    path('kanban/tarefa/nova/', views.criar_tarefa, name='criar_tarefa'),
    path('kanban/tarefa/nova/<int:coluna_id>/', views.criar_tarefa, name='criar_tarefa_coluna'),
    path('kanban/tarefa/<int:task_id>/', views.detalhe_tarefa, name='detalhe_tarefa'),
    path('kanban/tarefa/<int:task_id>/editar/', views.editar_tarefa, name='editar_tarefa'),
    path('kanban/tarefa/<int:task_id>/excluir/', views.excluir_tarefa, name='excluir_tarefa'),
    path('kanban/tarefa/mover/<int:task_id>/', views.mover_tarefa, name='mover_tarefa'),
    path('kanban/coluna/mover/<int:coluna_id>/', views.mover_coluna, name='mover_coluna'),
    path('kanban/marcar_andamento/<int:task_id>/', views.marcar_andamento, name='marcar_andamento'),
    path('kanban/finalizar/<int:task_id>/', views.finalizar, name='finalizar'),
    path('kanban/desfinalizar/<int:task_id>/', views.desfinalizar, name='desfinalizar'),
    path('kanban/registrar_quantidade/<int:task_id>/', views.registrar_quantidade, name='registrar_quantidade'),

    # --- Rotas de Controle de Ponto ---
    path('ponto/', views.controle_ponto, name='controle_ponto'),
    path('ponto/bater/', views.bater_ponto, name='bater_ponto'),
    path('ponto/abonar-dia/', views.abonar_dia, name='abonar_dia'),
    path('ponto/remover-abono/<int:abono_id>/', views.remover_abono_dia, name='remover_abono_dia'),
    path('ponto/configurar-periodo/', views.configurar_periodo_mes, name='configurar_periodo_mes'),

    # --- Rotas de Clientes ---
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/adicionar/', views.adicionar_cliente, name='adicionar_cliente'),
    path('clientes/<int:pk>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:pk>/excluir/', views.excluir_cliente, name='excluir_cliente'),

    # --- Rotas de Fornecedores ---
    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/adicionar/', views.adicionar_fornecedor, name='adicionar_fornecedor'),
    path('fornecedores/<int:pk>/', views.detalhe_fornecedor, name='detalhe_fornecedor'),
    path('fornecedores/<int:pk>/editar/', views.editar_fornecedor, name='editar_fornecedor'),
    path('fornecedores/<int:pk>/excluir/', views.excluir_fornecedor, name='excluir_fornecedor'),
]
