import os
import io
import segno
from PIL import Image, ImageDraw

def generate_qr_code(data, filename, logo_path='static/logo.png', folder='static/qr'):
    """
        Generates a QR code,
        And embeds a logo.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, f"{filename}.png")

    qr_buffer = io.BytesIO()
    segno.make(data, error='h').save(qr_buffer, kind='png', scale=10)
    qr_buffer.seek(0)

    qr_img = Image.open(qr_buffer).convert('RGB')
    img_width, img_height = qr_img.size

    # logo
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = img_height // 4
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

        mask = Image.new("L", logo.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)

        box = (
            (img_width - logo.size[0]) // 2,
            (img_height - logo.size[1]) // 2
        )

        qr_img.paste(logo, box, mask)

    qr_img.save(filepath)
    return filepath
