from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def compress_image(image_field, quality=85, max_width=1920, max_height=1080):
    """
    Comprime uma imagem mantendo a proporção e qualidade.

    Args:
        image_field: Campo ImageField do Django
        quality: Qualidade JPEG (0-100), padrão 85
        max_width: Largura máxima em pixels, padrão 1920
        max_height: Altura máxima em pixels, padrão 1080

    Returns:
        InMemoryUploadedFile: Imagem comprimida pronta para salvar
    """
    if not image_field:
        return None

    # Abre a imagem
    img = Image.open(image_field)

    # Converte para RGB se for PNG com transparência ou outro formato
    if img.mode in ('RGBA', 'LA', 'P'):
        # Cria fundo branco para PNGs transparentes
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Redimensiona mantendo proporção se necessário
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    # Salva em buffer
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)

    # Cria novo arquivo Django
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{image_field.name.split('.')[0]}.jpg",
        'image/jpeg',
        sys.getsizeof(output),
        None
    )
