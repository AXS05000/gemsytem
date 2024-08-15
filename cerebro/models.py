from django.db import models
from colaboradores.models import Colaboradores

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
        return f"{self.conhecimento_geral}"


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
        return f"{self.consulta_conhecimento}"


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
        return f"{self.experiencia}"


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
        return f"{self.aprendizado}"


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
        return f"{self.personalidade}"


class Atuais_Demandas(models.Model):
    STATUS_CHOICES = [
        ("P", "Pendente"),
        ("F", "Finalizada"),
    ]

    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="atuais_demandas_colaborador",
        verbose_name="Atuais Demandas do Colaborador",
    )
    atuais_demandas = models.TextField(blank=True, null=True)
    # Tarefas dadas pelo Supervisor

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default="P",
        verbose_name="Status da Tarefa",
    )

    def __str__(self):
        return f"{self.atuais_demandas} - {self.get_status_display()}"


class Mesa_de_trabalho(models.Model):
    colaborador = models.ForeignKey(
        Colaboradores,
        on_delete=models.CASCADE,
        related_name="mesas_de_trabalho_colaborador",
        verbose_name="Mesas de Trabalho do Colaborador",
    )
    utils = models.TextField(blank=True, null=True)
    views = models.TextField(blank=True, null=True)
    urls = models.TextField(blank=True, null=True)
    forms = models.TextField(blank=True, null=True)
    admin = models.TextField(blank=True, null=True)
    views = models.TextField(blank=True, null=True)
    models = models.TextField(blank=True, null=True)

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
        return f"{self.sugestoes}"


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
        return f"{self.tokens}"
