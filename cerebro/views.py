import openai
from django.shortcuts import render, get_object_or_404, redirect
from .models import Atuais_Demandas, Mesa_de_trabalho, Colaboradores
from github_app.utils import atualizar_arquivos_github
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from .forms import AjustarTarefaForm
from django.db.models import Sum
from .models import (
    Conhecimento,
    Consulta_De_Conhecimento,
    Experiencia,
    Aprendizado,
    Personalidade,
    Atuais_Demandas,
    Mesa_de_trabalho,
    Sugestoes,
    Custo,
)


class AtribuirTarefaView(View):
    def post(self, request, *args, **kwargs):
        atualizar_arquivos_github()
        print("Arquivos do GitHub Atualizados.")
        tarefa = request.POST.get("tarefa")
        colaboradores_ids = request.POST.getlist("colaboradores")
        incluir_github_files = request.POST.get("incluir_github_files") == "on"

        for colaborador_id in colaboradores_ids:
            colaborador = get_object_or_404(Colaboradores, id=colaborador_id)

            # Verifica se já existe uma mesa de trabalho para aquele colaborador e exclui a existente
            Mesa_de_trabalho.objects.filter(colaborador=colaborador).delete()

            if incluir_github_files:
                prompt_contexto = (
                    f"Você está trabalhando em um projeto Django que já está em andamento. "
                    f"Os arquivos atuais do sistema estão disponíveis para sua consulta. Sua tarefa é realizar a seguinte tarefa: {tarefa}. "
                    f"Certifique-se de considerar os arquivos existentes e realizar as modificações necessárias. "
                    f"Distribua as alterações corretamente entre models, views, urls, forms, admin e utils, conforme necessário. "
                    f"Salve o código correspondente em cada campo apropriado."
                )
            else:
                prompt_contexto = (
                    f"Você está trabalhando em um projeto Django. Sua tarefa é criar "
                    f"os arquivos necessários apenas para a parte de aplicativos (apps) "
                    f"de acordo com a descrição a seguir: {tarefa}. "
                    f"Por favor, gere os arquivos necessários e distribua corretamente entre "
                    f"models, views, urls, forms, admin e utils. "
                    f"Salve o código correspondente em cada campo apropriado."
                )

            demanda = Atuais_Demandas.objects.create(
                colaborador=colaborador,
                atuais_demandas=prompt_contexto,
                incluir_github_files=incluir_github_files,
            )

            demanda.processar_tarefa()

            demanda_qa = Atuais_Demandas.objects.create(
                colaborador_id=1,
                atuais_demandas=f"Avaliar tarefa '{tarefa}' do colaborador {colaborador.nome_do_colaborador}",
            )

            revisar_tarefa_qa(
                qa_id=1, colaborador_id=colaborador.id, tarefa_id=demanda_qa.id
            )

        return HttpResponseRedirect(reverse("wallet"))


def revisar_tarefa_qa(qa_id, colaborador_id, tarefa_id):
    qa = get_object_or_404(Colaboradores, id=qa_id)
    colaborador = get_object_or_404(Colaboradores, id=colaborador_id)
    tarefa = get_object_or_404(Atuais_Demandas, id=tarefa_id)

    try:
        mesa = Mesa_de_trabalho.objects.filter(colaborador=colaborador).latest("id")
    except Mesa_de_trabalho.DoesNotExist:
        print(f"Nenhuma mesa de trabalho encontrada para o colaborador: {colaborador}")
        return

    conhecimentos = Conhecimento.objects.filter(colaborador=qa).values_list(
        "conhecimento_geral", flat=True
    )
    experiencias = Experiencia.objects.filter(colaborador=qa).values_list(
        "experiencia", flat=True
    )
    aprendizados = Aprendizado.objects.filter(colaborador=qa).values_list(
        "aprendizado", flat=True
    )
    consulta_conhecimento = Consulta_De_Conhecimento.objects.filter(
        colaborador=qa
    ).values_list("consulta_conhecimento", flat=True)
    personalidade = (
        Personalidade.objects.filter(colaborador=qa)
        .values_list("personalidade", flat=True)
        .first()
    )

    contexto_adicional = ""

    if conhecimentos:
        contexto_conhecimento = " ".join(conhecimentos)
        contexto_adicional += f"Você tem esses conhecimentos: {contexto_conhecimento}. "

    if experiencias:
        contexto_experiencia = " ".join(experiencias)
        contexto_adicional += f"Você também possui essa experiência profissional: {contexto_experiencia}. "

    if aprendizados:
        contexto_aprendizado = " ".join(aprendizados)
        contexto_adicional += f"Neste contexto, o seu chefe deu as seguintes observações que devem ser seguidas: {contexto_aprendizado}. "

    if consulta_conhecimento:
        contexto_consulta = " ".join(consulta_conhecimento)
        contexto_adicional += f"Para sua referência, aqui estão alguns exemplos de trabalhos já realizados: {contexto_consulta}. "

    print("Contexto adicional montado para o QA.")
    print("QA analisando a tarefa...")

    response = openai.ChatCompletion.create(
        api_key=qa.api_key,
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um QA da GS especializado em revisão de desenvolvimento Django."
                    "Analise o trabalho realizado pelo colaborador de acordo com a descrição da tarefa e o código abaixo."
                    "Responda apenas com a palavra 'correto' ou 'incorreto', seguida de um ponto e vírgula (;), e depois coloque suas observações."
                    f"{contexto_adicional} "
                    f"Sempre fale em primeira pessoa e seu estilo de comunicação deve ser: {personalidade}."
                    f"Observação importante: O colaborador só realiza trabalhos de back-end, no caso ele só tem autorização de realizar códigos que possam ser escritos no models, views, urls, forms, admin e utils de app django. Verifique também se não tem alguma parte do código faltando, alguma importação de biblioteca funcionando, um dos seus principais objetivos é deixar o código funcional."
                ),
            },
            {
                "role": "user",
                "content": f"Tarefa: {tarefa.atuais_demandas}\n\nCódigo:\n{mesa.mesa}",
            },
        ],
        max_tokens=10500,
    )

    resultado = response["choices"][0]["message"]["content"]
    print("Revisão da tarefa pelo QA concluída.")

    status_qa, observacoes_qa = resultado.split(";", 1)
    status_qa = status_qa.strip().lower()

    if status_qa == "correto":
        tarefa_qa = Atuais_Demandas.objects.get(id=tarefa_id)
        tarefa_qa.status = "F"
        tarefa_qa.save()

        tarefa_colaborador = Atuais_Demandas.objects.filter(
            colaborador=colaborador
        ).latest("id")
        tarefa_colaborador.status = "F"
        tarefa_colaborador.save()

        mesa.anotacoes = f"Observações do QA: {observacoes_qa.strip()}"
        mesa.save()

        print(f"Tarefa finalizada com sucesso pelo QA: {qa.nome_do_colaborador}")

    elif mesa.versao_revisada > 5 and status_qa == "incorreto":
        print("Atingido o limite de revisões, quinta vez. Finalizando tarefa.")
        tarefa_qa = Atuais_Demandas.objects.get(id=tarefa_id)
        tarefa_qa.status = "F"
        tarefa_qa.save()

        tarefa_colaborador = Atuais_Demandas.objects.filter(
            colaborador=colaborador
        ).latest("id")
        tarefa_colaborador.status = "F"
        tarefa_colaborador.save()

        mesa.anotacoes = f"Finalizado: {observacoes_qa.strip()} - A tarefa foi finalizada devido ao colaborador não atingir o objetivo em 5 revisões."
        mesa.save()

        print("Tarefa finalizada após a oitava revisão sem sucesso.")

    else:
        tarefa.status = "P"
        tarefa.save()

        mesa.anotacoes = f"Observações do QA: {observacoes_qa.strip()}"
        mesa.save()

        tarefa_qa = Atuais_Demandas.objects.get(id=tarefa_id)
        tarefa_qa.status = "P"
        tarefa_qa.save()

        mesa.incrementar_versao()  # New line

        print(f"Tarefa revisada pelo QA com correções: {qa.nome_do_colaborador}")
        tarefa.revisar_tarefa_com_ajustes(colaborador=colaborador)
        print("Solicitando nova revisão do QA após ajustes...")
        revisar_tarefa_qa(qa_id, colaborador_id, tarefa_id)


def atribuir_tarefa_form(request):
    colaboradores = Colaboradores.objects.filter(
        id__in=[4, 5]
    )  # IDs do Ricardo e Leonardo
    return render(request, "atribuir_tarefa.html", {"colaboradores": colaboradores})


class AjustarTarefaView(View):
    def get(self, request, *args, **kwargs):
        form = AjustarTarefaForm()
        return render(request, "ajustar_tarefa.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = AjustarTarefaForm(request.POST)
        if form.is_valid():
            colaborador = form.cleaned_data["colaborador"]
            tarefa = form.cleaned_data["tarefa"]
            ajuste = form.cleaned_data["ajuste"]

            # Salvar os ajustes na mesa de trabalho do colaborador
            try:
                mesa = Mesa_de_trabalho.objects.filter(colaborador=colaborador).latest(
                    "id"
                )
            except Mesa_de_trabalho.DoesNotExist:
                mesa = Mesa_de_trabalho.objects.create(colaborador=colaborador, mesa="")

            # Alterado para salvar os ajustes na coluna 'anotacoes' em vez de 'mesa'
            mesa.anotacoes = (
                (mesa.anotacoes or "")
                + f"\n\nRealize também o ajustes solicitados pelo usuario, ele tem prioridade casa algum pedido seja conflintante com o do QA:\n{ajuste}"
            )
            mesa.save()

            # Chamar a função para revisar a tarefa com os ajustes
            tarefa.revisar_tarefa_com_ajustes(colaborador=colaborador)

            return redirect(reverse("ajustar_tarefa"))

        return render(request, "ajustar_tarefa.html", {"form": form})


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"


class ProfileView(TemplateView):
    template_name = "pages/profile.html"


class SignInView(TemplateView):
    template_name = "pages/sign-in.html"


class SignUpView(TemplateView):
    template_name = "pages/sign-up.html"


class TablesView(TemplateView):
    template_name = "pages/tables.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["colaboradores"] = Colaboradores.objects.all()
        return context


class WalletView(TemplateView):
    template_name = "pages/wallet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["colaboradores"] = Colaboradores.objects.all()
        return context


class WalletView(TemplateView):
    template_name = "pages/wallet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calcula o total de tokens de todos os colaboradores e formata o número
        total_tokens = Custo.objects.aggregate(total=Sum("tokens"))["total"] or 0
        formatted_total_tokens = "{:,}".format(total_tokens).replace(",", ".")

        # Prepara os dados para o gráfico
        colaboradores = Colaboradores.objects.all()
        labels = [
            colaborador.nome_do_colaborador.split()[0] for colaborador in colaboradores
        ]
        data = [
            Custo.objects.filter(colaborador=colaborador).aggregate(
                total=Sum("tokens")
            )["total"]
            or 0
            for colaborador in colaboradores
        ]

        # Coleta as mesas de trabalho e as anotações de cada colaborador
        mesas = {
            mesa.colaborador.id: {
                "mesa": (
                    mesa.mesa.strip()
                    if mesa.mesa
                    else "Sem mesa de trabalho disponível"
                ),
                "anotacoes": (
                    mesa.anotacoes.strip()
                    if mesa.anotacoes
                    else "Sem anotações disponíveis"
                ),
            }
            for mesa in Mesa_de_trabalho.objects.all()
        }

        context["total_tokens"] = formatted_total_tokens
        context["labels"] = labels
        context["data"] = data
        context["colaboradores"] = colaboradores
        context["mesas"] = mesas  # Adiciona mesas e anotações ao contexto
        return context
