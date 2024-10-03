from django.urls import path
from .views import (
    atualizar_tarefas,
    Profile_TasksView,
    concluir_tarefas_clickup,
    atualizar_tarefas_clickup,
)

urlpatterns = [
    path("atualizar-tarefas/", atualizar_tarefas, name="atualizar_tarefas"),
    path("profile-tasks/", Profile_TasksView.as_view(), name="profile_tasks"),
    path(
        "concluir-tarefas/", concluir_tarefas_clickup, name="concluir_tarefas_clickup"
    ),
    path(
        "atualizar-tarefas-clickup/",
        atualizar_tarefas_clickup,
        name="atualizar_tarefas_clickup",
    ),
]
