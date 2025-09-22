from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('estoque/', views.lista_estoque, name='lista_estoque'),
    path('estoque/adicionar/', views.adicionar_item, name='adicionar_item'),
    path('estoque/<int:pk>/gerenciar/', views.gerenciar_item, name='gerenciar_item'),
    path('estoque/<int:pk>/retirar/', views.retirar_item, name='retirar_item'),
    path('estoque/<int:pk>/adicionar-estoque/', views.adicionar_estoque, name='adicionar_estoque'),
    path('estoque/<int:pk>/excluir/', views.excluir_item, name='excluir_item'),
    path('recebimento/registrar/', views.registrar_recebimento, name='registrar_recebimento'),
]