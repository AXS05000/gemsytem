from django.db import models


# Create your models here.
class GitHubFiles(models.Model):
    models_file = models.TextField(null=True, blank=True)
    views_file = models.TextField(null=True, blank=True)
    urls_file = models.TextField(null=True, blank=True)
    forms_file = models.TextField(null=True, blank=True)
    utils_file = models.TextField(null=True, blank=True)
    admin_file = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Arquivos do GitHub salvos em {self.created_at}"


class GitHubToken(models.Model):
    token = models.CharField(max_length=255)
    description = models.CharField(
        max_length=100, null=True, blank=True
    )  # Opcional: descrição para identificar o token
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GitHub Token criado em {self.created_at} - {self.description or 'Sem descrição'}"
