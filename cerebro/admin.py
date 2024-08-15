from django.contrib import admin

from .models import (
    Conhecimento,
    Consulta_De_Conhecimento,
    Experiencia,
    Aprendizado,
    Personalidade,
    Atuais_Demandas,
    Mesa_de_trabalho,
    Sugestoes,
    Custo,
)

admin.site.register(Conhecimento)
admin.site.register(Consulta_De_Conhecimento)
admin.site.register(Experiencia)
admin.site.register(Aprendizado)
admin.site.register(Personalidade)
admin.site.register(Atuais_Demandas)
admin.site.register(Mesa_de_trabalho)
admin.site.register(Sugestoes)
admin.site.register(Custo)
