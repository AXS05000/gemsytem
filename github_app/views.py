from django.shortcuts import render
from .utils import fetch_github_files
from .models import GitHubToken


def import_github_files(request):
    # Buscando o token mais recente no banco de dados
    github_token = GitHubToken.objects.latest("created_at")
    token = github_token.token  # Token obtido do banco de dados
    repo_name = "AXS05000/gemsytem"

    # Chama a função para importar os arquivos
    fetch_github_files(repo_name, token)

    return render(request, "import_complete.html")
