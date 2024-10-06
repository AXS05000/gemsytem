from django.contrib import admin

from .models import (
    TarefaClickUp,
    Compromisso,
    TarefaNormal,
)


admin.site.register(TarefaClickUp)
admin.site.register(Compromisso)
admin.site.register(TarefaNormal)
