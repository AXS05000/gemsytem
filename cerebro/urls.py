from django.urls import path
from .views import (
    AtribuirTarefaView,
    atribuir_tarefa_form,
    DashboardView,
    ProfileView,
    SignInView,
    SignUpView,
    TablesView,
    WalletView,
    AjustarTarefaView,
)

urlpatterns = [
    path("atribuir-tarefa/", AtribuirTarefaView.as_view(), name="atribuir_tarefa"),
    path("atribuir-tarefa-form/", atribuir_tarefa_form, name="atribuir_tarefa_form"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("sign-in/", SignInView.as_view(), name="sign_in"),
    path("sign-up/", SignUpView.as_view(), name="sign_up"),
    path("tables/", TablesView.as_view(), name="tables"),
    path("wallet/", WalletView.as_view(), name="wallet"),
    path("ajustar-tarefa/", AjustarTarefaView.as_view(), name="ajustar_tarefa"),
]
