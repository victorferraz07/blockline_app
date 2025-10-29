# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_gastocaixainterno_enviado_financeiro'),
    ]

    operations = [
        migrations.AddField(
            model_name='gastoviagem',
            name='categoria',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Categoria'),
        ),
        migrations.AddField(
            model_name='gastoviagem',
            name='nota_fiscal',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Número da Nota Fiscal'),
        ),
    ]
