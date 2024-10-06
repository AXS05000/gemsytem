from django.http import JsonResponse
from .services import buscar_tarefas_pendentes
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from .models import TarefaClickUp, Compromisso, CursoUdemy
import requests
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from .forms import UdemyAuthForm
from django.shortcuts import render, redirect


@login_required
def atualizar_tarefas(request):
    usuario = request.user  # Pega o usuário logado
    buscar_tarefas_pendentes(usuario)
    return JsonResponse({"status": "Tarefas atualizadas com sucesso!"})


@login_required
def atualizar_tarefas_clickup(request):
    usuario = request.user
    buscar_tarefas_pendentes(
        usuario
    )  # Função que atualiza as tarefas no banco de dados
    return redirect("profile_tasks")  # Redireciona de volta para a página de perfil


class Profile_TasksView(TemplateView):
    template_name = "pages/profile-tasks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        # Buscar cursos da Udemy via API e atualizar no banco de dados
        self.atualizar_cursos_udemy()

        # Obter cursos do banco de dados
        context["cursos_udemy"] = CursoUdemy.objects.all()

        return context

    def atualizar_cursos_udemy(self):
        url = "https://www.udemy.com/api-2.0/courses/"
        headers = {
            "Authorization": f"Bearer {settings.UDEMY_API_TOKEN}",  # Configurar o token da API da Udemy
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            cursos_data = response.json()["results"]
            for curso in cursos_data:
                nome = curso["title"]
                progresso = curso[
                    "completion_percentage"
                ]  # Exemplo de campo para progresso

                CursoUdemy.objects.update_or_create(
                    nome=nome,
                    defaults={
                        "progresso": progresso,
                        "data_inicio": curso.get("start_date", None),
                        "data_conclusao": curso.get("end_date", None),
                    },
                )
        else:
            print(f"Erro ao buscar cursos da Udemy: {response.status_code}")


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


@login_required
def udemy_auth(request):
    if request.method == "POST":
        form = UdemyAuthForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data["client_id"]
            client_secret = form.cleaned_data["client_secret"]

            # URL da Udemy para obter o token
            url = "https://www.udemy.com/api-2.0/auth/token/"

            # Fazer requisição para obter o Access Token
            data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }

            response = requests.post(url, data=data)

            if response.status_code == 200:
                access_token = response.json().get("access_token")

                # Atualizar o usuário logado com o token e os dados do cliente
                usuario = request.user
                usuario.udemy_access_token = access_token
                usuario.udemy_client_id = client_id
                usuario.udemy_client_secret = client_secret
                usuario.save()

                messages.success(request, "Token da Udemy obtido e salvo com sucesso!")
                return redirect(
                    "profile_tasks"
                )  # Redirecionar para o perfil após salvar
            else:
                messages.error(
                    request,
                    f"Erro ao obter o token: {response.status_code} - {response.text}",
                )
    else:
        form = UdemyAuthForm()

    return render(request, "pages/udemy_auth.html", {"form": form})
