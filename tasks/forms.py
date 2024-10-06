# forms.py
from django import forms


class UdemyAuthForm(forms.Form):
    client_id = forms.CharField(label="ID do Cliente", max_length=255)
    client_secret = forms.CharField(
        label="Segredo do Cliente", max_length=255, widget=forms.PasswordInput
    )
