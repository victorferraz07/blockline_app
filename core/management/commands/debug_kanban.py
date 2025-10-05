from django.core.management.base import BaseCommand
from django.db.models import Sum
from core.models import Task, TaskQuantidadeFeita

class Command(BaseCommand):
    help = 'Debug dados do Kanban - mostra tasks e quantidades'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== DEBUG KANBAN ===\n'))

        all_tasks = Task.objects.all()
        total_geral = 0

        for task in all_tasks:
            # Pega todas as quantidades feitas para este task
            quantidades = task.quantidades_feitas.all()
            soma = task.quantidades_feitas.aggregate(total=Sum('quantidade'))['total'] or 0
            total_geral += soma

            self.stdout.write(f'\n📋 Task: {task.titulo}')
            self.stdout.write(f'   Meta: {task.quantidade_meta}')
            self.stdout.write(f'   Produzido: {soma}')
            self.stdout.write(f'   Registros de quantidade ({quantidades.count()}):')

            for qtd in quantidades:
                self.stdout.write(f'      - {qtd.quantidade} unidades por {qtd.usuario} em {qtd.data.strftime("%d/%m/%Y %H:%M")}')

        self.stdout.write(self.style.SUCCESS(f'\n\n✅ TOTAL GERAL PRODUZIDO: {total_geral}'))
        self.stdout.write(self.style.WARNING(f'📊 Total de Tasks: {all_tasks.count()}'))
        self.stdout.write(self.style.WARNING(f'📊 Total de registros TaskQuantidadeFeita: {TaskQuantidadeFeita.objects.count()}'))
