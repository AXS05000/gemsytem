from django.contrib import admin

from .models import (
    TarefaClickUp,
    Compromisso,
)


admin.site.register(TarefaClickUp)
admin.site.register(Compromisso)
