from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from core.models import RequisicaoCompra, PerfilUsuario


class Command(BaseCommand):
    help = 'Verifica boletos próximos do vencimento e envia alertas por email'

    def handle(self, *args, **options):
        from core.models import ParcelaBoleto

        self.stdout.write(self.style.WARNING('=== VERIFICAÇÃO DE BOLETOS ===\n'))

        hoje = timezone.now().date()
        alertas_enviados = 0

        # Buscar parcelas não pagas
        parcelas_pendentes = ParcelaBoleto.objects.filter(
            pago=False,
            data_vencimento__gte=hoje
        ).select_related('requisicao')

        for parcela in parcelas_pendentes:
            req = parcela.requisicao
            dias_aviso = req.dias_aviso_pagamento or 3

            # Calcular data do alerta (X dias antes do vencimento)
            data_alerta = parcela.data_vencimento - timedelta(days=dias_aviso)

            # Se hoje >= data_alerta e hoje <= vencimento, enviar alerta
            if hoje >= data_alerta and hoje <= parcela.data_vencimento:
                dias_restantes = (parcela.data_vencimento - hoje).days

                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Boleto: {req.item} - Parcela {parcela.numero_parcela} - Vence em {dias_restantes} dia(s)'
                    )
                )

                self.enviar_alerta_email(req, parcela, dias_restantes)
                alertas_enviados += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Verificação concluída. {alertas_enviados} alerta(s) enviado(s).')
        )

    def parsear_datas_vencimento(self, dias_str, hoje):
        """
        Converte string de datas/dias em lista de datas de vencimento.
        Aceita dois formatos:
        - Datas completas: "2025-01-15, 2025-02-15, 2025-03-15"
        - Dias do mês: "15, 30, 45"
        """
        datas = []
        partes = dias_str.split(',')

        for parte in partes:
            parte = parte.strip()

            # Tentar parsear como data completa (YYYY-MM-DD)
            if '-' in parte and len(parte) >= 8:
                try:
                    data_vencimento = datetime.strptime(parte, '%Y-%m-%d').date()
                    # Apenas incluir datas futuras ou de hoje
                    if data_vencimento >= hoje:
                        datas.append(data_vencimento)
                    continue
                except ValueError:
                    pass

            # Se não for data completa, tentar como dia do mês
            numeros = ''.join(filter(str.isdigit, parte))
            if numeros:
                dia_vencimento = int(numeros)
                data_vencimento = self.calcular_proximo_vencimento(hoje, dia_vencimento)
                datas.append(data_vencimento)

        return datas

    def parsear_dias(self, dias_str):
        """Converte string '15, 30, 45' em lista [15, 30, 45]"""
        dias = []
        for parte in dias_str.split(','):
            parte = parte.strip()
            # Tentar extrair números (ignora texto como "29 de fevereiro")
            numeros = ''.join(filter(str.isdigit, parte))
            if numeros:
                dias.append(int(numeros))
        return dias

    def calcular_proximo_vencimento(self, hoje, dia_vencimento):
        """Calcula próxima data de vencimento baseado no dia do mês"""
        ano = hoje.year
        mes = hoje.month

        # Se o dia já passou neste mês, pegar próximo mês
        if hoje.day > dia_vencimento:
            mes += 1
            if mes > 12:
                mes = 1
                ano += 1

        # Tratar dias inválidos (ex: 31 em mês com 30 dias)
        try:
            data_vencimento = datetime(ano, mes, dia_vencimento).date()
        except ValueError:
            # Se dia inválido, usar último dia do mês
            if mes == 12:
                proximo_mes = 1
                proximo_ano = ano + 1
            else:
                proximo_mes = mes + 1
                proximo_ano = ano
            data_vencimento = datetime(proximo_ano, proximo_mes, 1).date() - timedelta(days=1)

        return data_vencimento

    def enviar_alerta_email(self, requisicao, parcela, dias_restantes):
        """Envia email de alerta para usuários do financeiro"""
        # Buscar usuários do financeiro
        perfis_financeiro = PerfilUsuario.objects.filter(is_financeiro=True).select_related('usuario')

        if not perfis_financeiro.exists():
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhum usuário do financeiro cadastrado!')
            )
            return

        emails_destino = [perfil.usuario.email for perfil in perfis_financeiro if perfil.usuario.email]

        if not emails_destino:
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhum usuário do financeiro tem email cadastrado!')
            )
            return

        # Montar mensagem
        assunto = f'⚠️ Alerta: Boleto vencendo em {dias_restantes} dia(s) - {requisicao.item}'

        fornecedor = requisicao.fornecedor.nome if requisicao.fornecedor else (
            requisicao.fornecedor_nome_digitado or 'Não informado'
        )

        mensagem = f"""
Olá, equipe do Financeiro!

Este é um alerta automático sobre um boleto próximo do vencimento:

📋 Item: {requisicao.item}
📝 Descrição: {requisicao.descricao}
🔢 Parcela: {parcela.numero_parcela}/{requisicao.quantidade_parcelas or '?'}
💰 Valor da Parcela: R$ {parcela.valor}
🏢 Fornecedor: {fornecedor}
📅 Data de Vencimento: {parcela.data_vencimento.strftime('%d/%m/%Y')}
⏰ Dias Restantes: {dias_restantes} dia(s)

Status da Requisição: {requisicao.get_status_display()}

---
Acesse o sistema para marcar como pago: https://picsart.com.br/blockline/requisicoes/

Este é um email automático. Não responda.
        """

        try:
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                emails_destino,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email enviado para {len(emails_destino)} destinatário(s)')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao enviar email: {str(e)}')
            )
