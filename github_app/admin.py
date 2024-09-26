from django.contrib import admin

from .models import (
    GitHubFiles,
    GitHubToken,
)

admin.site.register(GitHubFiles)
admin.site.register(GitHubToken)
