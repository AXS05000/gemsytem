from django.urls import path
from .views import AtribuirTarefaView, atribuir_tarefa_form, ver_mesas

urlpatterns = [
    path("atribuir-tarefa/", AtribuirTarefaView.as_view(), name="atribuir_tarefa"),
    path("atribuir-tarefa-form/", atribuir_tarefa_form, name="atribuir_tarefa_form"),
    path("ver-mesas/", ver_mesas, name="ver_mesas"),
]
