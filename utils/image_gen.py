import io
import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size):
    # Ubuntu VPS par pre-installed fonts ki list
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_table_image(title, headers, rows):
    width = 800
    header_h = 60
    row_h = 50
    padding = 40

    height = padding*2 + header_h + (len(rows) * row_h) + 60

    bg_color = '#1C1F26'
    card_color = '#252A34'
    text_primary = '#FFFFFF'
    text_secondary = '#8B949E'
    accent_color = '#3390EC'

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    font_title = get_font(34)
    font_header = get_font(22)
    font_row = get_font(20)
    font_watermark = get_font(16)

    draw.text((padding, padding), title, fill=text_primary, font=font_title)

    card_y = padding + 60
    card_h = header_h + (len(rows) * row_h)
    draw.rounded_rectangle([padding, card_y, width-padding, card_y+card_h], radius=15, fill=card_color)

    cols_x = [padding + 20, padding + 120, width - 250]
    for i, h in enumerate(headers):
        draw.text((cols_x[i], card_y + 15), h, fill=text_secondary, font=font_header)

    draw.line([padding, card_y + header_h, width-padding, card_y + header_h], fill="#3A4150", width=2)

    y_offset = card_y + header_h
    for row in rows:
        draw.text((cols_x[0], y_offset + 15), str(row[0]), fill=text_secondary, font=font_row)
        draw.text((cols_x[1], y_offset + 15), str(row[1]), fill=accent_color, font=font_row) 
        draw.text((cols_x[2], y_offset + 15), str(row[2]), fill=text_primary, font=font_row)

        draw.line([padding, y_offset + row_h, width-padding, y_offset + row_h], fill="#3A4150", width=1)
        y_offset += row_h

    # Strictly applying ANYSNAP branding
    draw.text((width/2, height - 30), "Powered by ANYSNAP", fill=text_secondary, font=font_watermark, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf