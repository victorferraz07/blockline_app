# config/urls.py
from django.contrib import admin
# Adicione a importação do 'include'
from django.urls import path, include
# Importe as configurações e a função static
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta linha diz: "Qualquer URL que comece com 'estoque/', 
    # envie para ser resolvida pelo arquivo de URLs do app 'core'."
    path('estoque/', include('core.urls')),
]

# Adicione esta linha MÁGICA no final do arquivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
