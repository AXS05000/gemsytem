from django.db import models
from colaboradores.models import Colaboradores
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
    status = models.CharField(
        max_length=1,
        choices=[("P", "Pendente"), ("F", "Finalizada")],
        default="P",
        verbose_name="Status da Tarefa",
    )

    def processar_tarefa(self):
        colaborador = self.colaborador

        # Recuperar conhecimentos, experiências, aprendizados e personalidade do colaborador
        conhecimentos = Conhecimento.objects.filter(
            colaborador=colaborador
        ).values_list("conhecimento_geral", flat=True)
        experiencias = Experiencia.objects.filter(colaborador=colaborador).values_list(
            "experiencia", flat=True
        )
        aprendizados = Aprendizado.objects.filter(colaborador=colaborador).values_list(
            "aprendizado", flat=True
        )
        personalidade = (
            Personalidade.objects.filter(colaborador=colaborador)
            .values_list("personalidade", flat=True)
            .first()
        )

        # Montar o contexto adicional
        contexto_conhecimento = " ".join(conhecimentos)
        contexto_experiencia = " ".join(experiencias)
        contexto_aprendizado = " ".join(aprendizados)
        contexto_adicional = (
            f"Além dos seus conhecimentos em Django, você tem esses conhecimentos: {contexto_conhecimento}. "
            f"Você também possui essa experiência profissional: {contexto_experiencia}. "
            f"Neste contexto, o seu chefe deu as seguintes observações que devem ser seguidas: {contexto_aprendizado}."
        )

        # Usando a API da OpenAI para processar a tarefa com o modelo gpt-4-turbo
        response = openai.ChatCompletion.create(
            api_key=colaborador.api_key,
            model="gpt-4-turbo",
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
                        f"Seu estilo de comunicação deve ser: {personalidade}."
                    ),
                },
                {"role": "user", "content": self.atuais_demandas},
            ],
            max_tokens=2500,
        )

        resultado = response["choices"][0]["message"]["content"]

        # Salvando todo o resultado na coluna 'mesa'
        mesa = Mesa_de_trabalho.objects.create(
            colaborador=colaborador,
            mesa=resultado,
        )

        # Calcular e registrar o custo em tokens
        tokens_usados = response["usage"]["total_tokens"]
        Custo.objects.create(
            colaborador=colaborador,
            tokens=tokens_usados,
        )

        # Gerar sugestões de melhorias baseadas no resultado da tarefa
        sugestao_response = openai.ChatCompletion.create(
            api_key=colaborador.api_key,
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um colaborador da GS especializado em desenvolvimento Django. "
                        "Baseado nos seus conhecimentos, experiências, aprendizados e no código abaixo, forneça sugestões de melhorias."
                        f"{contexto_adicional} "
                        f"Seu estilo de comunicação deve ser: {personalidade}."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Analise o seguinte código e forneça sugestões de melhorias:\n{resultado}",
                },
            ],
            max_tokens=2500,
        )

        sugestao = sugestao_response["choices"][0]["message"]["content"]

        # Salvando as sugestões na tabela Sugestoes
        Sugestoes.objects.create(
            colaborador=colaborador,
            sugestoes=sugestao,
        )

        # Atualiza o status da demanda
        self.status = "F"
        self.save()

        return mesa

    def __str__(self):
        return (
            f"{self.colaborador} - {self.atuais_demandas} - {self.get_status_display()}"
        )


class Mesa_de_trabalho(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="mesas_de_trabalho_colaborador",
        verbose_name="Mesas de Trabalho do Colaborador",
    )
    mesa = models.TextField(blank=True, null=True)

    # Local onde será entregue seus trabalhos
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
