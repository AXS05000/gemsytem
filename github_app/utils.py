from github import Github
from .models import GitHubFiles, GitHubToken


def fetch_github_files(repo_name, token):
    g = Github(token)  # Seu token de autenticação no GitHub
    repo = g.get_repo(repo_name)

    # Defina os caminhos dos arquivos no repositório GitHub
    files_to_fetch = {
        "models_file": "cerebro/models.py",
        "views_file": "cerebro/views.py",
        "urls_file": "cerebro/urls.py",
        "forms_file": "cerebro/forms.py",
        "utils_file": "cerebro/utils.py",
        "admin_file": "cerebro/admin.py",
    }

    github_files = GitHubFiles()

    # Itera sobre os arquivos e salva o conteúdo nas respectivas colunas da model
    for field, file_path in files_to_fetch.items():
        try:
            file_content = repo.get_contents(file_path).decoded_content.decode("utf-8")
            setattr(github_files, field, file_content)
        except Exception as e:
            print(f"Erro ao buscar {file_path}: {e}")
            setattr(github_files, field, None)

    # Salva o objeto no banco de dados
    github_files.save()


def atualizar_arquivos_github():
    # Buscando o token mais recente no banco de dados
    github_token = GitHubToken.objects.latest("created_at")
    token = github_token.token  # Token obtido do banco de dados
    repo_name = "AXS05000/gemsytem"

    # Chama a função para importar os arquivos
    fetch_github_files(repo_name, token)
