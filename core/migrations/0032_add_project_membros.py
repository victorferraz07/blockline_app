from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_notificacao'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='membros',
            field=models.ManyToManyField(
                blank=True,
                related_name='projetos_participando',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Membros',
            ),
        ),
    ]
