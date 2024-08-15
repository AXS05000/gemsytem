from django.shortcuts import render, get_object_or_404
from .models import Atuais_Demandas, Mesa_de_trabalho, Colaboradores
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View


class AtribuirTarefaView(View):
    def post(self, request, *args, **kwargs):
        tarefa = request.POST.get("tarefa")
        colaboradores_ids = request.POST.getlist("colaboradores")

        for colaborador_id in colaboradores_ids:
            colaborador = get_object_or_404(Colaboradores, id=colaborador_id)

            # Adicionando o contexto ao prompt
            prompt_contexto = (
                f"Você está trabalhando em um projeto Django. Sua tarefa é criar "
                f"os arquivos necessários apenas para a parte de aplicativos (apps) "
                f"de acordo com a descrição a seguir: {tarefa}. "
                f"Por favor, gere os arquivos necessários e distribua corretamente entre "
                f"models, views, urls, forms, admin e utils. "
                f"Salve o código correspondente em cada campo apropriado."
            )

            # Criar a demanda para o colaborador
            demanda = Atuais_Demandas.objects.create(
                colaborador=colaborador,
                atuais_demandas=prompt_contexto,
            )

            # Processar a tarefa
            demanda.processar_tarefa()

            # Criar uma demanda para o QA para revisar a tarefa
            Atuais_Demandas.objects.create(
                colaborador_id=1,  # ID fixo para o André Gonçalves (QA)
                atuais_demandas=f"Avaliar tarefa '{tarefa}' do colaborador {colaborador.nome_do_colaborador}",
            )

        return HttpResponseRedirect(reverse("atribuir_tarefa_form"))


def atribuir_tarefa_form(request):
    colaboradores = Colaboradores.objects.filter(
        id__in=[4, 5]
    )  # IDs do Ricardo e Leonardo
    return render(request, "atribuir_tarefa.html", {"colaboradores": colaboradores})


def ver_mesas(request):
    mesas = Mesa_de_trabalho.objects.all()
    return render(request, "ver_mesas.html", {"mesas": mesas})
