"""
Script para gerar ícones temporários do PWA Blockline
Execute: python generate_icons.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Configurações
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
OUTPUT_DIR = "core/static/icons"
BACKGROUND_COLOR = (79, 70, 229)  # Indigo #4F46E5
TEXT_COLOR = (255, 255, 255)  # Branco
BORDER_RADIUS = 0.15  # 15% de bordas arredondadas

def create_rounded_rectangle(size, radius_percent=0.15):
    """Cria uma máscara para bordas arredondadas"""
    img = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(img)
    radius = int(size * radius_percent)
    draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill=255)
    return img

def generate_icon(size):
    """Gera um ícone com a letra B"""
    # Criar imagem
    img = Image.new('RGB', (size, size), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Tentar usar fonte do sistema
    try:
        # Tamanho da fonte proporcional ao ícone
        font_size = int(size * 0.6)
        # Tentar diferentes fontes
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",  # Windows
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
        ]

        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break

        if font is None:
            # Fallback para fonte padrão
            font = ImageFont.load_default()

    except Exception as e:
        print(f"Aviso: Usando fonte padrão ({e})")
        font = ImageFont.load_default()

    # Desenhar letra "B"
    text = "B"

    # Calcular posição central
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) / 2 - bbox[0]
    y = (size - text_height) / 2 - bbox[1]

    # Desenhar texto
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)

    # Aplicar bordas arredondadas (opcional)
    # mask = create_rounded_rectangle(size, BORDER_RADIUS)
    # output = Image.new('RGB', (size, size), BACKGROUND_COLOR)
    # output.paste(img, (0, 0))
    # output.putalpha(mask)

    return img

def main():
    """Gera todos os ícones necessários"""
    # Criar diretório se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🎨 Gerando ícones PWA para Blockline...")
    print(f"📁 Diretório: {OUTPUT_DIR}")
    print()

    for size in ICON_SIZES:
        filename = f"icon-{size}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)

        print(f"  Gerando {filename}...", end=" ")

        try:
            icon = generate_icon(size)
            icon.save(filepath, "PNG", optimize=True)
            print(f"✅ {os.path.getsize(filepath) // 1024}KB")
        except Exception as e:
            print(f"❌ Erro: {e}")

    print()
    print("✅ Ícones gerados com sucesso!")
    print()
    print("📝 Próximos passos:")
    print("1. Rode o servidor Django: python manage.py runserver")
    print("2. Abra Chrome DevTools (F12) → Aba 'Application' → 'Manifest'")
    print("3. Verifique se os ícones aparecem corretamente")
    print("4. Teste a instalação do PWA")
    print()
    print("💡 Dica: Para ícones profissionais, veja ICON_GENERATION.md")

if __name__ == "__main__":
    main()
