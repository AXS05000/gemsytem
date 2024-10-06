from django.http import JsonResponse
from .services import buscar_tarefas_pendentes
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from .models import TarefaClickUp, Compromisso
import requests
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
import base64


@login_required
def atualizar_tarefas(request):
    usuario = request.user  # Pega o usuário logado
    buscar_tarefas_pendentes(usuario)
    return JsonResponse({"status": "Tarefas atualizadas com sucesso!"})


@login_required
def atualizar_tarefas_clickup(request):
    usuario = request.user
    buscar_tarefas_pendentes(usuario)
    return redirect("profile_tasks")


class Profile_TasksView(TemplateView):
    template_name = "pages/profile-tasks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        hoje = timezone.now().date()

        # Filtrar tarefas com data inicial até hoje
        context["tarefas"] = (
            TarefaClickUp.objects.filter(
                usuario=usuario,
                data_inicial__lte=hoje,
            )
            .exclude(data_inicial__isnull=True)
            .order_by("data_inicial")
        )

        # Filtrar compromissos com data até hoje
        context["compromissos"] = Compromisso.objects.filter(
            data_inicio__lte=hoje
        ).order_by("data_inicio")

        # # Obter cursos da Udemy do banco de dados
        # context["cursos_udemy"] = CursoUdemy.objects.all()

        return context


class TarefasFuturasView(TemplateView):
    template_name = "pages/profile-tasks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        # Obtendo a data de amanhã
        amanha = timezone.now().date() + timezone.timedelta(days=1)

        # Filtrar tarefas com data inicial a partir de amanhã
        context["tarefas"] = (
            TarefaClickUp.objects.filter(
                usuario=usuario,
                data_inicial__gte=amanha,  # Mostra tarefas com data inicial a partir de amanhã
            )
            .exclude(data_inicial__isnull=True)
            .order_by("data_inicial")
        )
        return context


@require_POST
def concluir_tarefas_clickup(request):
    usuario = request.user
    tarefas_ids = request.POST.getlist(
        "tarefas_concluidas"
    )  # IDs das tarefas selecionadas

    for tarefa_id in tarefas_ids:
        # Concluir a tarefa no ClickUp
        concluir_tarefa_clickup(tarefa_id, usuario.clickup_api_token)

        # Excluir a tarefa do sistema
        TarefaClickUp.objects.filter(tarefa_id=tarefa_id, usuario=usuario).delete()

    return redirect("profile_tasks")


def concluir_tarefa_clickup(tarefa_id, clickup_token):
    url = f"https://api.clickup.com/api/v2/task/{tarefa_id}"

    headers = {
        "Authorization": clickup_token,
    }

    data = {
        "status": "complete",  # Status de conclusão
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code != 200:
        print(
            f"Erro ao concluir tarefa {tarefa_id}: {response.status_code} - {response.text}"
        )


class CompromissoCreateView(CreateView):
    model = Compromisso
    fields = ["nome", "data_inicio", "hora_inicio", "data_final", "hora_final", "local"]
    template_name = "pages/compromisso_form.html"
    success_url = reverse_lazy("profile_tasks")


class CompromissoUpdateView(UpdateView):
    model = Compromisso
    fields = ["nome", "data_inicio", "hora_inicio", "data_final", "hora_final", "local"]
    template_name = "pages/compromisso_form.html"
    success_url = reverse_lazy("profile_tasks")
