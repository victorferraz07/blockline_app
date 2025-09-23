from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # --- Rotas de Estoque ---
    path('estoque/', views.lista_estoque, name='lista_estoque'),
    path('estoque/adicionar/', views.adicionar_item, name='adicionar_item'),
    path('estoque/<int:pk>/gerenciar/', views.gerenciar_item, name='gerenciar_item'),
    path('estoque/<int:pk>/retirar/', views.retirar_item, name='retirar_item'),
    path('estoque/<int:pk>/adicionar-estoque/', views.adicionar_estoque, name='adicionar_estoque'),
    path('estoque/<int:pk>/excluir/', views.excluir_item, name='excluir_item'),
    
    # --- Rotas de Recebimento ---
    path('recebimento/', views.lista_recebimentos, name='lista_recebimentos'),
    path('recebimento/registrar/', views.registrar_recebimento, name='registrar_recebimento'),
    path('recebimento/<int:pk>/', views.detalhe_recebimento, name='detalhe_recebimento'),
    path('recebimento/<int:pk>/editar/', views.editar_recebimento, name='editar_recebimento'),

    # --- Rotas de Produto ---
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('produtos/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('produtos/<int:pk>/', views.detalhe_produto, name='detalhe_produto'),
    path('produtos/<int:pk>/editar/', views.editar_produto, name='editar_produto'),
]