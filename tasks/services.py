from django.utils.timezone import make_aware
from .models import TarefaClickUp
import requests
from django.conf import settings
from datetime import datetime
from usuarios.models import CustomUsuario


def buscar_tarefas_pendentes(usuario):
    clickup_token = usuario.clickup_api_token
    clickup_list_id = usuario.clickup_list_id

    if not clickup_token or not clickup_list_id:
        raise ValueError(
            "Usuário não possui token de API ou List ID do ClickUp configurados."
        )

    url = f"https://api.clickup.com/api/v2/list/{clickup_list_id}/task"

    headers = {
        "Authorization": clickup_token,
    }

    params = {
        "status": "open",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        tarefas_pendentes = response.json()["tasks"]

        ids_pendentes = [tarefa["id"] for tarefa in tarefas_pendentes]

        # Atualizando ou criando as tarefas pendentes no banco de dados e vinculando ao usuário
        for tarefa in tarefas_pendentes:
            nome = tarefa["name"]
            data_inicial = tarefa.get("start_date")
            data_vencimento = tarefa.get("due_date")

            if data_inicial:
                data_inicial = make_aware(
                    datetime.fromtimestamp(int(data_inicial) / 1000)
                )
            if data_vencimento:
                data_vencimento = make_aware(
                    datetime.fromtimestamp(int(data_vencimento) / 1000)
                )

            tarefa_id = tarefa["id"]

            TarefaClickUp.objects.update_or_create(
                tarefa_id=tarefa_id,
                defaults={
                    "nome": nome,
                    "data_inicial": data_inicial,
                    "data_vencimento": data_vencimento,
                    "status": "open",
                    "usuario": usuario,  # Vinculando ao usuário logado
                },
            )

        # Verificar e excluir as tarefas concluídas
        tarefas_no_banco = TarefaClickUp.objects.filter(
            usuario=usuario
        )  # Filtrar por usuário

        for tarefa in tarefas_no_banco:
            if tarefa.tarefa_id not in ids_pendentes:
                tarefa.delete()
    else:
        print(f"Erro ao buscar tarefas: {response.status_code} - {response.text}")
