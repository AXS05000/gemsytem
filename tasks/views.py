from django.http import JsonResponse
from .services import buscar_tarefas_pendentes
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .models import TarefaClickUp


@login_required
def atualizar_tarefas(request):
    usuario = request.user  # Pega o usuário logado
    buscar_tarefas_pendentes(usuario)
    return JsonResponse({"status": "Tarefas atualizadas com sucesso!"})


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
