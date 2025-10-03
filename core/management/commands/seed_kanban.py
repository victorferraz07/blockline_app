from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import KanbanColumn, Task

class Command(BaseCommand):
    help = 'Popula o Kanban com colunas e cards iniciais.'

    def handle(self, *args, **options):
        # Colunas padrão
        colunas = [
            {'nome': 'A Fazer', 'cor': '#f3f4f6', 'ordem': 0},
            {'nome': 'Em Progresso', 'cor': '#fef08a', 'ordem': 1},
            {'nome': 'Concluído', 'cor': '#bbf7d0', 'ordem': 2},
        ]
        KanbanColumn.objects.all().delete()
        Task.objects.all().delete()
        col_objs = []
        for c in colunas:
            col = KanbanColumn.objects.create(**c)
            col_objs.append(col)
        # Cards exemplo
        Task.objects.create(coluna=col_objs[0], titulo='Planejar produção', descricao='Definir metas e recursos', quantidade=0, ordem=0)
        Task.objects.create(coluna=col_objs[0], titulo='Separar materiais', descricao='Checar estoque e separar itens', quantidade=0, ordem=1)
        Task.objects.create(coluna=col_objs[1], titulo='Montagem em andamento', descricao='Equipe executando montagem', quantidade=2, ordem=0)
        Task.objects.create(coluna=col_objs[2], titulo='Revisão finalizada', descricao='Produto revisado e aprovado', quantidade=5, ordem=0)
        self.stdout.write(self.style.SUCCESS('Kanban populado com colunas e cards iniciais!'))
