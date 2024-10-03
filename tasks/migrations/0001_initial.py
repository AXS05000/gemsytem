# Generated by Django 5.0.8 on 2024-10-03 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TarefaClickUp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('data_inicial', models.DateTimeField()),
                ('data_vencimento', models.DateTimeField()),
                ('tarefa_id', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
