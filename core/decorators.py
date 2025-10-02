"""
Decorators personalizados para segurança e controle de acesso
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def superuser_required(view_func):
    """
    Decorator que exige que o usuário seja superuser
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_user_empresa(user):
    """
    Retorna a primeira empresa disponível para o usuário.
    Em sistema multi-empresa real, isso deve vir do perfil do usuário.
    """
    from core.models import Empresa

    # Para superusuários, retorna todas as empresas
    if user.is_superuser:
        return Empresa.objects.all()

    # Para usuários normais, retorna empresas do perfil (futuro)
    # Por enquanto, retorna a primeira empresa disponível
    primeira_empresa = Empresa.objects.first()
    if primeira_empresa:
        return Empresa.objects.filter(pk=primeira_empresa.pk)

    return Empresa.objects.none()


def filter_by_empresa(queryset, user, empresa_field='empresa'):
    """
    Filtra queryset pela empresa do usuário

    Args:
        queryset: QuerySet a ser filtrado
        user: Usuário atual
        empresa_field: Nome do campo de empresa no modelo (default: 'empresa')

    Returns:
        QuerySet filtrado
    """
    empresas = get_user_empresa(user)
    filter_kwargs = {f'{empresa_field}__in': empresas}
    return queryset.filter(**filter_kwargs)
