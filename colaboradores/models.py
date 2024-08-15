from django.db import models


class Colaboradores(models.Model):
    nome_do_colaborador = models.CharField(
        max_length=100, verbose_name="Nome do Colaborador", null=True, blank=True
    )
    cargo = models.CharField(
        max_length=100, verbose_name="Cargo do Colaborador", null=True, blank=True
    )
    api_key = models.CharField("Chave API", max_length=255, blank=True, null=True)
    idade = models.IntegerField(null=True, blank=True)
    aparencia = models.TextField(null=True, blank=True)
    foto = models.ImageField(
        upload_to="fotos_colaboradores/",
        verbose_name="Foto do Colaborador",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.nome_do_colaborador} - {self.cargo}"
