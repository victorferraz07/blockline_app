# core/urls.py
from django.urls import path
# Vamos importar nossas views daqui a pouco
from . import views

urlpatterns = [
    # A URL '' (vazia) corresponde à raiz de '/estoque/'.
    # Quando acessada, ela chamará a view 'lista_estoque' que ainda vamos criar.
    # 'name' é um apelido para a URL, muito útil no futuro.
    path('', views.lista_estoque, name='lista_estoque'),
]