# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_gastocaixainterno_nota_fiscal'),
    ]

    operations = [
        migrations.AddField(
            model_name='gastocaixainterno',
            name='enviado_financeiro',
            field=models.BooleanField(default=False, verbose_name='Enviado ao Financeiro'),
        ),
    ]
