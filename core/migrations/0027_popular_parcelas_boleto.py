from django.db import migrations
from datetime import datetime


def popular_parcelas_boleto(apps, schema_editor):
    RequisicaoCompra = apps.get_model('core', 'RequisicaoCompra')
    ParcelaBoleto = apps.get_model('core', 'ParcelaBoleto')

    requisicoes_boleto = RequisicaoCompra.objects.filter(
        forma_pagamento='boleto'
    ).exclude(dias_pagamento__isnull=True).exclude(dias_pagamento='')

    for req in requisicoes_boleto:
        # Parsear dias_pagamento
        dias_str = req.dias_pagamento.strip()
        datas_vencimento = []

        for parte in dias_str.split(','):
            parte = parte.strip()

            # Tentar como data completa (YYYY-MM-DD)
            if '-' in parte and len(parte) >= 8:
                try:
                    data = datetime.strptime(parte, '%Y-%m-%d').date()
                    datas_vencimento.append(data)
                except ValueError:
                    pass

        if not datas_vencimento:
            continue

        # Calcular valor da parcela
        valor_total = req.preco_real or req.preco_estimado or 0
        quantidade = len(datas_vencimento)
        valor_parcela = valor_total / quantidade if quantidade > 0 else 0

        # Criar parcelas
        for i, data_vencimento in enumerate(datas_vencimento, start=1):
            ParcelaBoleto.objects.create(
                requisicao=req,
                numero_parcela=i,
                data_vencimento=data_vencimento,
                valor=valor_parcela,
                pago=False  # Assume não pagas
            )


def reverter_parcelas(apps, schema_editor):
    ParcelaBoleto = apps.get_model('core', 'ParcelaBoleto')
    ParcelaBoleto.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0026_parcelaboleto'),
    ]

    operations = [
        migrations.RunPython(popular_parcelas_boleto, reverter_parcelas),
    ]
