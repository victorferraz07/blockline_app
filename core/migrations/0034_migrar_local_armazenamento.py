from django.db import migrations


def copiar_local_para_posicao(apps, schema_editor):
    """
    Copia o valor de local_armazenamento para posicao_local
    em itens que ainda não possuem os novos campos preenchidos.
    Preserva todos os dados existentes sem deletar nada.
    """
    ItemEstoque = apps.get_model('core', 'ItemEstoque')
    itens = ItemEstoque.objects.filter(
        local_armazenamento__isnull=False,
        posicao_local__isnull=True,
    ).exclude(local_armazenamento='')
    for item in itens:
        item.posicao_local = item.local_armazenamento
        item.save(update_fields=['posicao_local'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_itemestoque_tipo_local_identificador_local_posicao_local'),
    ]

    operations = [
        migrations.RunPython(
            copiar_local_para_posicao,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
