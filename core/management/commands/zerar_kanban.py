from django.core.management.base import BaseCommand
from core.models import Task, TaskQuantidadeFeita, TaskHistorico, KanbanColumn

class Command(BaseCommand):
    help = 'Zera todos os dados do Kanban (Tasks, Quantidades, Histórico)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️  ATENÇÃO: Isso irá deletar TODOS os dados do Kanban!'))

        # Deletar quantidades feitas
        qtd_count = TaskQuantidadeFeita.objects.count()
        TaskQuantidadeFeita.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ Deletados {qtd_count} registros de TaskQuantidadeFeita'))

        # Deletar histórico
        hist_count = TaskHistorico.objects.count()
        TaskHistorico.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ Deletados {hist_count} registros de TaskHistorico'))

        # Deletar tasks
        task_count = Task.objects.count()
        Task.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ Deletados {task_count} Tasks'))

        # Deletar colunas
        col_count = KanbanColumn.objects.count()
        KanbanColumn.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ Deletadas {col_count} Colunas'))

        self.stdout.write(self.style.SUCCESS('\n✅ Kanban zerado com sucesso!'))
        self.stdout.write(self.style.WARNING('\n💡 Execute "python manage.py seed_kanban" para criar dados de exemplo'))
