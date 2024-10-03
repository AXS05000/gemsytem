import requests
from django.conf import settings
from .models import TarefaClickUp
from datetime import datetime
from django.utils.timezone import make_aware


CLICKUP_BASE_URL = "https://api.clickup.com/api/v2"


def buscar_tarefas_pendentes():
    url = f"{CLICKUP_BASE_URL}/list/{settings.CLICKUP_LIST_ID}/task"

    headers = {
        "Authorization": settings.CLICKUP_API_TOKEN,
    }

    # Pegando apenas tarefas pendentes
    params = {
        "status": "open",  # Filtro para pegar apenas tarefas pendentes
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        tarefas_pendentes = response.json()["tasks"]

        # Pegando os IDs das tarefas pendentes no ClickUp
        ids_pendentes = [tarefa["id"] for tarefa in tarefas_pendentes]

        # Atualizando ou criando as tarefas pendentes no banco de dados
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

            # Criando ou atualizando as tarefas no banco de dados
            TarefaClickUp.objects.update_or_create(
                tarefa_id=tarefa_id,
                defaults={
                    "nome": nome,
                    "data_inicial": data_inicial,
                    "data_vencimento": data_vencimento,
                    "status": "open",  # Se está na lista, é pendente (aberta)
                },
            )

        # Agora, verificar quais tarefas no banco não estão mais pendentes (concluídas)
        tarefas_no_banco = TarefaClickUp.objects.all()

        for tarefa in tarefas_no_banco:
            if tarefa.tarefa_id not in ids_pendentes:
                # Se o ID da tarefa não está mais na lista de pendentes, marque como concluída
                tarefa.status = "complete"
                tarefa.save()
    else:
        print(f"Erro ao buscar tarefas: {response.status_code} - {response.text}")
