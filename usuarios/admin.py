from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .forms import CustomUsuarioChangeForm, CustomUsuarioCreateForm
from .models import CustomUsuario


class CustomUsuarioCreateForm(UserCreationForm):
    class Meta:
        model = CustomUsuario
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "imagem_perfil",
        )
        field_order = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "imagem_perfil",
        ]


class CustomUsuarioChangeForm(UserChangeForm):
    class Meta:
        model = CustomUsuario
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "fone",
            "imagem_perfil",
        )


@admin.register(CustomUsuario)
class CustomUsuarioAdmin(UserAdmin):
    add_form = CustomUsuarioCreateForm
    form = CustomUsuarioChangeForm
    model = CustomUsuario
    list_display = ("first_name", "last_name", "email", "fone", "is_staff")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "api_key",
                    "clickup_api_token",
                    "clickup_list_id",
                )
            },
        ),
        (
            "Informações Pessoais",
            {"fields": ("first_name", "last_name", "fone", "imagem_perfil")},
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas Importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "imagem_perfil",
                    "api_key",
                ),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
