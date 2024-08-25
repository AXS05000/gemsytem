import openai
from django.shortcuts import render, get_object_or_404
from .models import Atuais_Demandas, Mesa_de_trabalho, Colaboradores
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
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
            demanda_qa = Atuais_Demandas.objects.create(
                colaborador_id=1,  # ID fixo para o André Gonçalves (QA)
                atuais_demandas=f"Avaliar tarefa '{tarefa}' do colaborador {colaborador.nome_do_colaborador}",
            )

            # Revisar a tarefa automaticamente após a execução do colaborador
            revisar_tarefa_qa(
                qa_id=1, colaborador_id=colaborador.id, tarefa_id=demanda_qa.id
            )

        return HttpResponseRedirect(reverse("atribuir_tarefa_form"))


def revisar_tarefa_qa(qa_id, colaborador_id, tarefa_id):
    qa = get_object_or_404(Colaboradores, id=qa_id)
    colaborador = get_object_or_404(Colaboradores, id=colaborador_id)
    tarefa = get_object_or_404(Atuais_Demandas, id=tarefa_id)

    # Recuperar o trabalho realizado na Mesa_de_trabalho
    mesa = get_object_or_404(Mesa_de_trabalho, colaborador=colaborador)

    # Recuperar conhecimentos, experiências, aprendizados, consulta e personalidade do QA
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

    # Montar o contexto adicional para o QA
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

    # Analisar o trabalho do colaborador usando a API da OpenAI
    print("QA analisando a tarefa...")
    response = openai.ChatCompletion.create(
        api_key=qa.api_key,
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um QA da GS especializado em revisão de desenvolvimento Django."
                    "Analise o trabalho realizado pelo colaborador de acordo com a descrição da tarefa e o código abaixo."
                    "Responda apenas com a palavra 'correto' ou 'incorreto', seguida de um ponto e vírgula (;), e depois coloque suas observações."
                    f"{contexto_adicional} "
                    f"Sempre fale em primeira pessoa e seu estilo de comunicação deve ser: {personalidade}."
                ),
            },
            {
                "role": "user",
                "content": f"Tarefa: {tarefa.atuais_demandas}\n\nCódigo:\n{mesa.mesa}",
            },
        ],
        max_tokens=2500,
    )

    resultado = response["choices"][0]["message"]["content"]
    print("Revisão da tarefa pelo QA concluída.")

    # Separar a primeira palavra (correto/incorreto) das observações
    status_qa, observacoes_qa = resultado.split(";", 1)
    status_qa = status_qa.strip().lower()

    if status_qa == "correto":
        # Se estiver correto, finalizar a tarefa e salvar observações
        tarefa.status = "F"
        tarefa.save()
        mesa.mesa += f"\n\nObservações do QA: {observacoes_qa.strip()}"
        mesa.save()
        print(f"Tarefa finalizada com sucesso pelo QA: {qa.nome_do_colaborador}")
    else:
        # Se estiver incorreto, deixar a tarefa pendente e adicionar as observações do QA
        tarefa.status = "P"  # Mantém a tarefa como pendente
        tarefa.save()
        mesa.mesa = f"Observações do QA: {observacoes_qa.strip()}\n\n{mesa.mesa}"
        mesa.save()
        print(f"Tarefa revisada pelo QA com correções: {qa.nome_do_colaborador}")


def atribuir_tarefa_form(request):
    colaboradores = Colaboradores.objects.filter(
        id__in=[4, 5]
    )  # IDs do Ricardo e Leonardo
    return render(request, "atribuir_tarefa.html", {"colaboradores": colaboradores})


def ver_mesas(request):
    mesas = Mesa_de_trabalho.objects.all()
    return render(request, "ver_mesas.html", {"mesas": mesas})
