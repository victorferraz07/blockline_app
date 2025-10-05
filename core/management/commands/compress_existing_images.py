from django.core.management.base import BaseCommand
from core.models import (
    ItemEstoque, Recebimento, ProdutoFabricado,
    ImagemItemEstoque, ImagemProdutoFabricado, ImagemExpedicao
)
from core.utils import compress_image
from django.core.files.base import ContentFile
import os


class Command(BaseCommand):
    help = 'Comprime todas as imagens existentes no banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a compressão sem salvar',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN - Nenhuma alteração será salva\n'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  ATENÇÃO: Isso irá comprimir TODAS as imagens existentes!\n'))

        total_compressed = 0
        total_size_before = 0
        total_size_after = 0

        # Comprimir ItemEstoque.foto_principal
        self.stdout.write('\n📦 Comprimindo fotos de ItemEstoque...')
        for item in ItemEstoque.objects.exclude(foto_principal=''):
            if item.foto_principal:
                try:
                    size_before = item.foto_principal.size
                    if not dry_run:
                        compressed = compress_image(item.foto_principal)
                        item.foto_principal.save(compressed.name, compressed, save=True)
                    size_after = item.foto_principal.size if not dry_run else size_before * 0.3  # Estimativa

                    total_size_before += size_before
                    total_size_after += size_after
                    total_compressed += 1

                    reduction = ((size_before - size_after) / size_before) * 100
                    self.stdout.write(f'  ✓ {item.nome}: {size_before/1024:.1f}KB → {size_after/1024:.1f}KB ({reduction:.1f}% redução)')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Erro ao comprimir {item.nome}: {e}'))

        # Comprimir Recebimento.foto_documento e foto_embalagem
        self.stdout.write('\n📋 Comprimindo fotos de Recebimento...')
        for receb in Recebimento.objects.all():
            if receb.foto_documento:
                try:
                    size_before = receb.foto_documento.size
                    if not dry_run:
                        compressed = compress_image(receb.foto_documento)
                        receb.foto_documento.save(compressed.name, compressed, save=True)
                    size_after = receb.foto_documento.size if not dry_run else size_before * 0.3

                    total_size_before += size_before
                    total_size_after += size_after
                    total_compressed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Erro: {e}'))

            if receb.foto_embalagem:
                try:
                    size_before = receb.foto_embalagem.size
                    if not dry_run:
                        compressed = compress_image(receb.foto_embalagem)
                        receb.foto_embalagem.save(compressed.name, compressed, save=True)
                    size_after = receb.foto_embalagem.size if not dry_run else size_before * 0.3

                    total_size_before += size_before
                    total_size_after += size_after
                    total_compressed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Erro: {e}'))

        # Comprimir ProdutoFabricado.foto_principal
        self.stdout.write('\n🏭 Comprimindo fotos de ProdutoFabricado...')
        for produto in ProdutoFabricado.objects.exclude(foto_principal=''):
            if produto.foto_principal:
                try:
                    size_before = produto.foto_principal.size
                    if not dry_run:
                        compressed = compress_image(produto.foto_principal)
                        produto.foto_principal.save(compressed.name, compressed, save=True)
                    size_after = produto.foto_principal.size if not dry_run else size_before * 0.3

                    total_size_before += size_before
                    total_size_after += size_after
                    total_compressed += 1

                    reduction = ((size_before - size_after) / size_before) * 100
                    self.stdout.write(f'  ✓ {produto.nome}: {size_before/1024:.1f}KB → {size_after/1024:.1f}KB ({reduction:.1f}% redução)')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Erro ao comprimir {produto.nome}: {e}'))

        # Comprimir ImagemItemEstoque
        self.stdout.write('\n🖼️  Comprimindo ImagemItemEstoque...')
        for img in ImagemItemEstoque.objects.all():
            if img.imagem:
                try:
                    size_before = img.imagem.size
                    if not dry_run:
                        compressed = compress_image(img.imagem)
                        img.imagem.save(compressed.name, compressed, save=True)
                    size_after = img.imagem.size if not dry_run else size_before * 0.3

                    total_size_before += size_before
                    total_size_after += size_after
                    total_compressed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Erro: {e}'))

        # Comprimir ImagemProdutoFabricado
        self.stdout.write('\n🖼️  Comprimindo ImagemProdutoFabricado...')
        for img in ImagemProdutoFabricado.objects.all():
            if img.imagem:
                try:
                    size_before = img.imagem.size
                    if not dry_run:
                        compressed = compress_image(img.imagem)
                        img.imagem.save(compressed.name, compressed, save=True)
                    size_after = img.imagem.size if not dry_run else size_before * 0.3

                    total_size_before += size_before
                    total_size_after += size_after
                    total_compressed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Erro: {e}'))

        # Comprimir ImagemExpedicao
        self.stdout.write('\n🚚 Comprimindo ImagemExpedicao...')
        for img in ImagemExpedicao.objects.all():
            if img.imagem:
                try:
                    size_before = img.imagem.size
                    if not dry_run:
                        compressed = compress_image(img.imagem)
                        img.imagem.save(compressed.name, compressed, save=True)
                    size_after = img.imagem.size if not dry_run else size_before * 0.3

                    total_size_before += size_before
                    total_size_after += size_after
                    total_compressed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Erro: {e}'))

        # Resumo final
        total_reduction = ((total_size_before - total_size_after) / total_size_before * 100) if total_size_before > 0 else 0

        self.stdout.write(self.style.SUCCESS(f'\n\n✅ Compressão concluída!'))
        self.stdout.write(f'📊 Total de imagens: {total_compressed}')
        self.stdout.write(f'📉 Tamanho antes: {total_size_before/1024/1024:.2f} MB')
        self.stdout.write(f'📈 Tamanho depois: {total_size_after/1024/1024:.2f} MB')
        self.stdout.write(self.style.SUCCESS(f'💾 Redução total: {total_reduction:.1f}% ({(total_size_before - total_size_after)/1024/1024:.2f} MB economizados)'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY-RUN: Nenhuma alteração foi salva. Execute sem --dry-run para comprimir de verdade.'))
