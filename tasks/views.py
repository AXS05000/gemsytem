from django.http import JsonResponse
from .services import buscar_tarefas_pendentes


def atualizar_tarefas(request):
    buscar_tarefas_pendentes()  # Chama a função que busca as tarefas no ClickUp
    return JsonResponse({"status": "Tarefas atualizadas com sucesso!"})
