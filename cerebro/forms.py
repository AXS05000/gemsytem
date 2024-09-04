from django import forms
from .models import Colaboradores, Atuais_Demandas


class AjustarTarefaForm(forms.Form):
    colaborador = forms.ModelChoiceField(
        queryset=Colaboradores.objects.filter(status="ativo"),
        label="Selecione o Colaborador",
        required=True,
    )
    tarefa = forms.ModelChoiceField(
        queryset=Atuais_Demandas.objects.filter(status="P"),
        label="Selecione a Tarefa",
        required=True,
    )
    ajuste = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": "Descreva os ajustes que deseja realizar"}
        ),
        label="Ajustes",
        required=True,
    )
