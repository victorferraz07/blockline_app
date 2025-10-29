# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_gastocaixainterno_gastoviagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='gastocaixainterno',
            name='nota_fiscal',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Número da Nota Fiscal'),
        ),
    ]
