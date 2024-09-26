from django.urls import path
from .views import import_github_files

urlpatterns = [
    path("importar-arquivos/", import_github_files, name="importar_arquivos"),
]
