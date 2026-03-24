from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_add_project_membros'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemestoque',
            name='tipo_local',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Tipo de Local'),
        ),
        migrations.AddField(
            model_name='itemestoque',
            name='identificador_local',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Identificador do Local'),
        ),
        migrations.AddField(
            model_name='itemestoque',
            name='posicao_local',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Posição / Subdivisão'),
        ),
    ]
