from django.urls import path
from .views import atualizar_tarefas

urlpatterns = [
    path("atualizar-tarefas/", atualizar_tarefas, name="atualizar_tarefas"),
]
