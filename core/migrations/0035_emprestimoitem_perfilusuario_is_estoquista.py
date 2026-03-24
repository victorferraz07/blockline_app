from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_migrar_local_armazenamento'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilusuario',
            name='is_estoquista',
            field=models.BooleanField(default=False, verbose_name='É Estoquista'),
        ),
        migrations.CreateModel(
            name='EmprestimoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(default=1, verbose_name='Quantidade')),
                ('prazo_devolucao', models.DateField(verbose_name='Prazo de Devolução')),
                ('status', models.CharField(choices=[('ativo', 'Emprestado'), ('devolvido', 'Devolvido'), ('atrasado', 'Atrasado')], default='ativo', max_length=20, verbose_name='Status')),
                ('data_emprestimo', models.DateTimeField(auto_now_add=True, verbose_name='Data do Empréstimo')),
                ('data_devolucao', models.DateTimeField(blank=True, null=True, verbose_name='Data de Devolução')),
                ('observacoes', models.TextField(blank=True, verbose_name='Observações')),
                ('notificacao_atraso_enviada', models.BooleanField(default=False)),
                ('emprestado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='emprestimos_concedidos', to=settings.AUTH_USER_MODEL, verbose_name='Emprestado por')),
                ('funcionario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='emprestimos_recebidos', to=settings.AUTH_USER_MODEL, verbose_name='Funcionário')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='emprestimos', to='core.itemestoque', verbose_name='Item')),
                ('tarefa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='emprestimos', to='core.projecttask', verbose_name='Tarefa Relacionada')),
            ],
            options={
                'verbose_name': 'Empréstimo de Item',
                'verbose_name_plural': 'Empréstimos de Itens',
                'ordering': ['-data_emprestimo'],
            },
        ),
    ]
