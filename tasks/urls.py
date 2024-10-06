from django.urls import path
from .views import (
    atualizar_tarefas,
    Profile_TasksView,
    concluir_tarefas_clickup,
    atualizar_tarefas_clickup,
    CompromissoCreateView,
    CompromissoUpdateView,
    TarefaNormalCreateView,
    TarefaNormalUpdateView,
)

urlpatterns = [
    path("atualizar-tarefas/", atualizar_tarefas, name="atualizar_tarefas"),
    path(
        "partitura-do-planejamento/", Profile_TasksView.as_view(), name="profile_tasks"
    ),
    path(
        "tarefas/nova/", TarefaNormalCreateView.as_view(), name="tarefa_normal_create"
    ),
    path(
        "tarefas/editar/<int:pk>/",
        TarefaNormalUpdateView.as_view(),
        name="tarefa_normal_edit",
    ),
    path(
        "concluir-tarefas-clickup/",
        concluir_tarefas_clickup,
        name="concluir_tarefas_clickup",
    ),
    path(
        "concluir-tarefas/", concluir_tarefas_clickup, name="concluir_tarefas_clickup"
    ),
    path(
        "atualizar-tarefas-clickup/",
        atualizar_tarefas_clickup,
        name="atualizar_tarefas_clickup",
    ),
    path(
        "compromissos/novo/", CompromissoCreateView.as_view(), name="compromisso_create"
    ),
    path(
        "compromissos/editar/<int:pk>/",
        CompromissoUpdateView.as_view(),
        name="compromisso_edit",
    ),
]
