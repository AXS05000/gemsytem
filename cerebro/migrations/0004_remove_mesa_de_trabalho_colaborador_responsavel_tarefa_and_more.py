# Generated by Django 5.0.8 on 2024-08-25 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cerebro', '0003_mesa_de_trabalho_colaborador_responsavel_tarefa_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mesa_de_trabalho',
            name='colaborador_responsavel_tarefa',
        ),
        migrations.RemoveField(
            model_name='mesa_de_trabalho',
            name='id_tarefa',
        ),
        migrations.AddField(
            model_name='mesa_de_trabalho',
            name='anotacoes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
