from django.http import JsonResponse
from .services import buscar_tarefas_pendentes
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from .models import TarefaClickUp, Compromisso, TarefaNormal
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

        # Verificar o parâmetro 'dias' na URL para compromissos e tarefas
        mostrar_proximos_30 = self.request.GET.get("dias", "7") == "30"
        mostrar_tarefas_futuras = self.request.GET.get("tarefas", "atuais") == "futuras"

        # Gerenciamento de compromissos
        if mostrar_proximos_30:
            # Mostrar compromissos dos próximos 30 dias após os 7 dias
            inicio_intervalo = hoje + timezone.timedelta(days=7)
            fim_intervalo = inicio_intervalo + timezone.timedelta(days=30)
            context["compromissos"] = Compromisso.objects.filter(
                usuario=usuario, data_inicio__range=[inicio_intervalo, fim_intervalo]
            ).order_by("data_inicio")
        else:
            # Padrão: Mostrar compromissos dos próximos 7 dias
            fim_intervalo = hoje + timezone.timedelta(days=7)
            context["compromissos"] = Compromisso.objects.filter(
                usuario=usuario, data_inicio__range=[hoje, fim_intervalo]
            ).order_by("data_inicio")

        # Gerenciamento de tarefas MB
        if mostrar_tarefas_futuras:
            # Mostrar tarefas futuras com data inicial a partir de amanhã
            amanha = hoje + timezone.timedelta(days=1)
            context["tarefas"] = (
                TarefaClickUp.objects.filter(
                    usuario=usuario,
                    data_inicial__gte=amanha,
                )
                .exclude(data_inicial__isnull=True)
                .order_by("data_inicial")
            )
        else:
            # Padrão: Mostrar tarefas com data inicial até hoje
            context["tarefas"] = (
                TarefaClickUp.objects.filter(
                    usuario=usuario,
                    data_inicial__lte=hoje,
                )
                .exclude(data_inicial__isnull=True)
                .order_by("data_inicial")
            )

        # Filtrar tarefas normais
        context["tarefas_normais"] = TarefaNormal.objects.filter(
            usuario=usuario,
        ).order_by("data_inicial")

        # Passar o valor atual de 'dias' e 'tarefas' para o contexto
        context["dias_filtro"] = 30 if mostrar_proximos_30 else 7
        context["tarefas_futuras"] = mostrar_tarefas_futuras

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


class TarefaNormalCreateView(CreateView):
    model = TarefaNormal
    template_name = "pages/tarefa_form.html"
    fields = ["nome", "data_inicial", "data_vencimento", "status"]
    success_url = reverse_lazy("profile_tasks")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class TarefaNormalUpdateView(UpdateView):
    model = TarefaNormal
    template_name = "pages/tarefa_form.html"
    fields = ["nome", "data_inicial", "data_vencimento", "status"]
    success_url = reverse_lazy("profile_tasks")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class CompromissoCreateView(CreateView):
    model = Compromisso
    fields = ["nome", "data_inicio", "hora_inicio", "data_final", "hora_final", "local"]
    template_name = "pages/compromisso_form.html"
    success_url = reverse_lazy("profile_tasks")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class CompromissoUpdateView(UpdateView):
    model = Compromisso
    fields = ["nome", "data_inicio", "hora_inicio", "data_final", "hora_final", "local"]
    template_name = "pages/compromisso_form.html"
    success_url = reverse_lazy("profile_tasks")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)
