from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

'''1º) include(usuarios.urls) -> precisa criar um arquivo urls.py dentro da pasta
   usuarios
   2º) No arquivo settings.py add o app usuarios em INSTALLED_APPS = ['usuarios']
   3º) Importar <from django.conf.urls.static import static> para url de midias
'''
'''urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('exames/', include('exames.urls')),
]'''

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('exames/', include('exames.urls')),
    path('empresarial/', include('empresarial.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)