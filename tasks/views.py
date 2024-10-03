from django.http import JsonResponse
from .services import buscar_tarefas_pendentes
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .models import TarefaClickUp
import requests
from django.shortcuts import redirect
from django.views.decorators.http import require_POST


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
        # Filtrando as tarefas do ClickUp pelo usuário logado e que tenham data_inicial preenchida
        context["tarefas"] = TarefaClickUp.objects.filter(usuario=usuario).exclude(
            data_inicial__isnull=True
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
