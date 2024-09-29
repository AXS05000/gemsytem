from github import Github
from .models import GitHubFiles, GitHubToken


def fetch_github_files(repo_name, token):
    g = Github(token)
    repo = g.get_repo(repo_name)

    # Defina os caminhos corretos dos arquivos no repositório GitHub
    files_to_fetch = {
        "models_file": "cerebro/models.py",  # Ajuste para o caminho correto
        "views_file": "cerebro/views.py",  # Ajuste para o caminho correto
        "urls_file": "cerebro/urls.py",  # Ajuste para o caminho correto
        "forms_file": "cerebro/forms.py",  # Ajuste para o caminho correto
        "utils_file": "cerebro/utils.py",  # O arquivo que pode não existir
        "admin_file": "cerebro/admin.py",  # Ajuste para o caminho correto
    }

    github_files = GitHubFiles()

    # Itera sobre os arquivos e tenta buscá-los
    for field, file_path in files_to_fetch.items():
        try:
            # Tenta buscar o arquivo do repositório
            file_content = repo.get_contents(file_path).decoded_content.decode("utf-8")
            setattr(github_files, field, file_content)
        except Exception as e:
            # Se o arquivo não existir (404), ignora o erro e continua
            if "404" in str(e):
                print(f"Arquivo não encontrado: {file_path}. Ignorando...")
                setattr(github_files, field, None)  # Deixa o campo vazio (None)
            else:
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
