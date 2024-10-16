from django.db import models
from colaboradores.models import Colaboradores
from github_app.models import GitHubFiles
import openai

#############################CONHECIMENTO###################################


class Conhecimento(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="conhecimentos_colaborador",
        verbose_name="Conhecimentos do Colaborador",
    )

    conhecimento_geral = models.TextField(blank=True, null=True)
    # Prompt de informação dos seus conhecimentos, como python, django e programação backend.

    def __str__(self):
        return f"{self.colaborador}"


class Consulta_De_Conhecimento(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="consulta_conhecimentos_colaborador",
        verbose_name="Consulta de Conhecimentos do Colaborador",
    )

    consulta_conhecimento = models.TextField(blank=True, null=True)
    # Informações como arquivos .py dos sistema já desenvolvidos para servir de consulta para ele replicar.

    def __str__(self):
        return f"{self.colaborador}"


class Experiencia(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="experiencias_colaborador",
        verbose_name="Experiências do Colaborador",
    )

    experiencia = models.TextField(blank=True, null=True)
    # Prompt para definir cargo Ex: Analista de Dados Senior

    def __str__(self):
        return f"{self.colaborador}"


class Aprendizado(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="aprendizados_colaborador",
        verbose_name="Aprendizados do Colaborador",
    )

    aprendizado = models.TextField(blank=True, null=True)
    # Aprendizados ensinados pelo QA e Supervisor.

    def __str__(self):
        return f"{self.colaborador}"


#############################PERSONALIDADE E DEMANDAS###################################


class Personalidade(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="personalidades_colaborador",
        verbose_name="Personalidades do Colaborador",
    )

    personalidade = models.TextField(blank=True, null=True)
    # Prompt para definir a personalidade do colaborador.

    def __str__(self):
        return f"{self.colaborador}"


class Atuais_Demandas(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="atuais_demandas_colaborador",
        verbose_name="Atuais Demandas do Colaborador",
    )
    atuais_demandas = models.TextField(blank=True, null=True)
    incluir_github_files = models.BooleanField(default=False)
    status = models.CharField(
        max_length=1,
        choices=[("P", "Pendente"), ("F", "Finalizada")],
        default="P",
        verbose_name="Status da Tarefa",
    )
    resumo_tarefa = models.TextField(blank=True, null=True)

    def analisar_e_resumir_tarefa(self):
        print("Iniciando análise e resumo da tarefa...")

        response = openai.ChatCompletion.create(
            api_key=self.colaborador.api_key,
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que resume tarefas de desenvolvimento.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Resuma a seguinte tarefa em poucas palavras, no maximo em 10 palavras: {self.atuais_demandas}"
                        "Desconsidere esse texto caso tenha 'Você está trabalhando em um projeto Django. Sua tarefa é criar os arquivos necessários apenas para a parte de aplicativos (apps) de acordo com a descrição a seguir:'"
                        "Por favor, gere os arquivos necessários e distribua corretamente entre models, views, urls, forms, admin e utils. Salve o código correspondente em cada campo apropriado.'"
                    ),
                },
            ],
            max_tokens=5000,
        )

        resumo = response["choices"][0]["message"]["content"].strip()
        self.resumo_tarefa = resumo
        self.save()

        print("Análise e resumo da tarefa concluídos.")

    def processar_tarefa(self, gerar_sugestoes=False):
        colaborador = self.colaborador
        print(f"Iniciando processamento da tarefa para o colaborador: {colaborador}")

        # Recuperar conhecimentos, experiências, aprendizados, consulta e personalidade do colaborador
        conhecimentos = Conhecimento.objects.filter(
            colaborador=colaborador
        ).values_list("conhecimento_geral", flat=True)
        experiencias = Experiencia.objects.filter(colaborador=colaborador).values_list(
            "experiencia", flat=True
        )
        aprendizados = Aprendizado.objects.filter(colaborador=colaborador).values_list(
            "aprendizado", flat=True
        )
        consulta_conhecimento = Consulta_De_Conhecimento.objects.filter(
            colaborador=colaborador
        ).values_list("consulta_conhecimento", flat=True)
        personalidade = (
            Personalidade.objects.filter(colaborador=colaborador)
            .values_list("personalidade", flat=True)
            .first()
        )

        # Montar o contexto adicional
        contexto_adicional = ""

        if conhecimentos:
            contexto_conhecimento = " ".join(conhecimentos)
            contexto_adicional += f"Além dos seus conhecimentos em Django, você tem esses conhecimentos: {contexto_conhecimento}. "

        if experiencias:
            contexto_experiencia = " ".join(experiencias)
            contexto_adicional += f"Você também possui essa experiência profissional: {contexto_experiencia}. "

        if aprendizados:
            contexto_aprendizado = " ".join(aprendizados)
            contexto_adicional += f"Neste contexto, o seu chefe deu as seguintes observações que devem ser seguidas: {contexto_aprendizado}. "

        if consulta_conhecimento:
            contexto_consulta = " ".join(consulta_conhecimento)
            contexto_adicional += f"Para sua referência, aqui estão alguns exemplos de trabalhos já realizados: {contexto_consulta}. "

        # Se a opção incluir_github_files estiver marcada, incluir os arquivos do GitHub no contexto
        if self.incluir_github_files:
            github_files = GitHubFiles.objects.latest(
                "created_at"
            )  # Busca os arquivos mais recentes do GitHub
            contexto_adicional += (
                f"Aqui estão os arquivos do projeto django em andamento:\n\n"
                f"models.py:\n{github_files.models_file}\n\n"
                f"views.py:\n{github_files.views_file}\n\n"
                f"urls.py:\n{github_files.urls_file}\n\n"
                f"forms.py:\n{github_files.forms_file}\n\n"
                f"utils.py:\n{github_files.utils_file}\n\n"
                f"admin.py:\n{github_files.admin_file}\n\n"
            )

        print("Contexto adicional montado.")

        if not gerar_sugestoes:
            # Usando a API da OpenAI para processar a tarefa com o modelo gpt-4o-2024-08-06
            print("Enviando tarefa para a API da OpenAI...")
            response = openai.ChatCompletion.create(
                api_key=colaborador.api_key,
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um colaborador da GS especializado em desenvolvimento Django."
                            "Responda exclusivamente com o código necessário para os arquivos do app Django especificados. "
                            "Inclua apenas código Python relacionado a models.py, forms.py, views.py, urls.py, admin.py, e utils.py."
                            "Não inclua templates html."
                            "Não inclua introduções, textos paralelos, orientações de importações, resumos, explicações ou notas, apenas o código puro dos arquivos em python."
                            f"{contexto_adicional} "
                            f"Sempre fale em primeira pessoa e seu estilo de comunicação deve ser: {personalidade}."
                            "Nas respostas sempre mostre os codigos completos, não abrevie nada. Mostre sempre as funções completas que foram ajustadas."
                        ),
                    },
                    {"role": "user", "content": self.atuais_demandas},
                ],
                max_tokens=2500,
            )

            resultado = response["choices"][0]["message"]["content"]
            print("Resposta da API recebida.")

            # Salvando todo o resultado na coluna 'mesa'
            mesa = Mesa_de_trabalho.objects.create(
                colaborador=colaborador,
                mesa=resultado,
            )
            print("Resultado salvo na mesa de trabalho.")

            # Calcular e registrar o custo em tokens
            tokens_usados = response["usage"]["total_tokens"]
            Custo.objects.create(
                colaborador=colaborador,
                tokens=tokens_usados,
            )
            print(f"Custo registrado: {tokens_usados} tokens usados.")

            # A tarefa não será finalizada aqui. O QA decidirá isso na revisão.
            print(
                f"Tarefa processada pelo colaborador {colaborador.nome_do_colaborador}, aguardando revisão do QA."
            )
            return mesa

        else:
            # Gerar sugestões de melhorias baseadas no resultado da tarefa após aprovação do QA
            print("Gerando sugestões de melhorias após aprovação do QA...")
            mesa = Mesa_de_trabalho.objects.filter(colaborador=colaborador).latest("id")
            sugestao_response = openai.ChatCompletion.create(
                api_key=colaborador.api_key,
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um colaborador da GS especializado em desenvolvimento Django. "
                            "Baseado nos seus conhecimentos, experiências, aprendizados e no código abaixo, forneça sugestões de melhorias."
                            f"{contexto_adicional} "
                            f"Sempre fale em primeira pessoa como se você tivesse realizado esse trabalho e seu estilo de comunicação deve ser: {personalidade}."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Analise o seguinte código e forneça sugestões de melhorias:\n{mesa.mesa}",
                    },
                ],
                max_tokens=10500,
            )

            sugestao = sugestao_response["choices"][0]["message"]["content"]
            print("Sugestões de melhorias geradas.")

            # Salvando as sugestões na tabela Sugestoes
            Sugestoes.objects.create(
                colaborador=colaborador,
                sugestoes=sugestao,
            )
            print("Sugestões de melhorias salvas.")

    def revisar_tarefa_com_ajustes(self, colaborador):
        print(f"Iniciando revisão da tarefa para o colaborador: {colaborador}")

        # Recuperar conhecimentos, experiências, aprendizados, consulta e personalidade do colaborador
        conhecimentos = Conhecimento.objects.filter(
            colaborador=colaborador
        ).values_list("conhecimento_geral", flat=True)
        experiencias = Experiencia.objects.filter(colaborador=colaborador).values_list(
            "experiencia", flat=True
        )
        aprendizados = Aprendizado.objects.filter(colaborador=colaborador).values_list(
            "aprendizado", flat=True
        )
        consulta_conhecimento = Consulta_De_Conhecimento.objects.filter(
            colaborador=colaborador
        ).values_list("consulta_conhecimento", flat=True)
        personalidade = (
            Personalidade.objects.filter(colaborador=colaborador)
            .values_list("personalidade", flat=True)
            .first()
        )

        # Recuperar a mesa de trabalho do colaborador
        try:
            mesa = Mesa_de_trabalho.objects.filter(colaborador=colaborador).latest("id")
        except Mesa_de_trabalho.DoesNotExist:
            print(
                f"Nenhuma mesa de trabalho encontrada para o colaborador: {colaborador}"
            )
            return

        # Recuperar as anotações do QA
        anotacoes_qa = mesa.anotacoes

        # Montar o contexto adicional incluindo as anotações do QA e o trabalho já realizado
        contexto_adicional = ""

        if conhecimentos:
            contexto_conhecimento = " ".join(conhecimentos)
            contexto_adicional += f"Além dos seus conhecimentos em Django, você tem esses conhecimentos: {contexto_conhecimento}. "

        if experiencias:
            contexto_experiencia = " ".join(experiencias)
            contexto_adicional += f"Você também possui essa experiência profissional: {contexto_experiencia}. "

        if aprendizados:
            contexto_aprendizado = " ".join(aprendizados)
            contexto_adicional += f"Neste contexto, o seu chefe deu as seguintes observações que devem ser seguidas: {contexto_aprendizado}. "

        if consulta_conhecimento:
            contexto_consulta = " ".join(consulta_conhecimento)
            contexto_adicional += f"Para sua referência, aqui estão alguns exemplos de trabalhos já realizados: {contexto_consulta}. "

        if anotacoes_qa:
            contexto_adicional += (
                f"O QA deixou as seguintes observações para revisão: {anotacoes_qa}. "
            )

        # Incluir o código já feito pelo colaborador
        contexto_adicional += (
            f"\nAqui está o que você já realizou até agora:\n{mesa.mesa}"
        )

        # Se a tarefa incluiu arquivos do GitHub, incluir os arquivos originais do GitHub no contexto
        if self.incluir_github_files:
            github_files = GitHubFiles.objects.latest("created_at")
            contexto_adicional += (
                f"\n\nAqui estão os arquivos originais do projeto Django que você está melhorando:\n\n"
                f"models.py:\n{github_files.models_file}\n\n"
                f"views.py:\n{github_files.views_file}\n\n"
                f"urls.py:\n{github_files.urls_file}\n\n"
                f"forms.py:\n{github_files.forms_file}\n\n"
                f"utils.py:\n{github_files.utils_file}\n\n"
                f"admin.py:\n{github_files.admin_file}\n\n"
            )

        print("Contexto adicional montado para revisão.")

        # Usando a API da OpenAI para revisar a tarefa com o modelo gpt-4o-2024-08-06
        print("Enviando tarefa revisada para a API da OpenAI...")
        response = openai.ChatCompletion.create(
            api_key=colaborador.api_key,
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um colaborador da GS especializado em desenvolvimento Django."
                        "Reveja o código abaixo com base nas observações do QA e faça os ajustes necessários, sem perder as informações que já estavam certas anteriormente."
                        "Digite novamente todos os códigos com os ajustes necessários com base nas observações do QA, inclua apenas código Python relacionado a models.py, forms.py, views.py, urls.py, admin.py, e utils.py."
                        "Não inclua templates html."
                        "Não inclua introduções, textos paralelos, orientações de importações, resumos, explicações ou notas, apenas o código puro dos arquivos em python."
                        f"{contexto_adicional} "
                        f"Sempre fale em primeira pessoa e seu estilo de comunicação deve ser: {personalidade}."
                    ),
                },
                {"role": "user", "content": self.atuais_demandas},
            ],
            max_tokens=10500,
        )

        resultado_revisao = response["choices"][0]["message"]["content"]
        print("Resposta da API para a revisão recebida.")

        # Adicionar as anotações do QA na 'mesa'
        if anotacoes_qa:
            mesa.mesa += f"\n\nAnotações do QA:\n{anotacoes_qa}"

        # Adicionar a nova versão revisada na coluna 'mesa' com número sequencial
        mesa.mesa += f"\n\nVersão {mesa.versao_revisada} Revisada:\n{resultado_revisao}"
        mesa.save()

        # Calcular e registrar o custo em tokens para a revisão
        tokens_usados_revisao = response["usage"]["total_tokens"]
        Custo.objects.create(
            colaborador=colaborador,
            tokens=tokens_usados_revisao,
        )
        print(
            f"Custo registrado para a revisão: {tokens_usados_revisao} tokens usados."
        )

        print(
            f"Tarefa revisada pelo colaborador {colaborador.nome_do_colaborador} com base nas observações do QA."
        )

    def __str__(self):
        return (
            f"{self.colaborador} - {self.get_status_display()} - {self.resumo_tarefa}"
        )


class Mesa_de_trabalho(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="mesas_de_trabalho_colaborador_criador",
        verbose_name="Mesas de Trabalho do Colaborador Criador",
    )
    mesa = models.TextField(blank=True, null=True)
    anotacoes = models.TextField(blank=True, null=True)
    versao_revisada = models.IntegerField(default=1)  # Nova coluna

    def incrementar_versao(self):
        self.versao_revisada += 1
        self.save()

    def __str__(self):
        return f"{self.colaborador}"


class Sugestoes(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="sugestoes_colaborador",
        verbose_name="Sugestões do Colaborador",
    )

    sugestoes = models.TextField(blank=True, null=True)
    # Sugestões de Melhoria onde ele da sugestões do que quer melhorar.

    def __str__(self):
        return f"{self.colaborador}"


class Custo(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="custos_colaborador",
        verbose_name="Custos do Colaborador",
    )

    tokens = models.IntegerField(blank=True, null=True)
    # Quantidade de Tokens usados por cada tarefa.

    def __str__(self):
        return f"{self.colaborador} - {self.tokens}"
