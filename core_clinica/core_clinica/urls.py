from django.contrib import admin
from django.urls import path
from gestao.api import api # Verifique se essa linha existe

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", api.urls), # O erro diz que o Django não está vendo isso aqui!
]