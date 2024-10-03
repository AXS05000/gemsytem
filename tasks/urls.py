from django.urls import path
from .views import atualizar_tarefas, Profile_TasksView

urlpatterns = [
    path("atualizar-tarefas/", atualizar_tarefas, name="atualizar_tarefas"),
    path("profile-tasks/", Profile_TasksView.as_view(), name="profile_tasks"),
]
