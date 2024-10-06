from django.urls import path
from .views import (
    atualizar_tarefas,
    Profile_TasksView,
    concluir_tarefas_clickup,
    atualizar_tarefas_clickup,
    TarefasFuturasView,
    CompromissoCreateView,
    CompromissoUpdateView,
)

urlpatterns = [
    path("atualizar-tarefas/", atualizar_tarefas, name="atualizar_tarefas"),
    path("profile-tasks/", Profile_TasksView.as_view(), name="profile_tasks"),
    path("tarefas-futuras/", TarefasFuturasView.as_view(), name="tarefas_futuras"),
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
