from django.db import models
from usuarios.models import CustomUsuario  # Importando o modelo de usuário


class TarefaClickUp(models.Model):
    nome = models.CharField(max_length=255)
    data_inicial = models.DateTimeField(null=True, blank=True)
    data_vencimento = models.DateTimeField(null=True, blank=True)
    tarefa_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    usuario = models.ForeignKey(
        CustomUsuario, on_delete=models.CASCADE
    )  # Relacionando com o usuário

    def __str__(self):
        return self.nome
