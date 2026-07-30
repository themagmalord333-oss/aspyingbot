import io
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

def get_font(size):
    font_path = "Roboto-Bold.ttf"
    # Auto-download font if not exists for premium look
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def create_table_image(title, headers, rows):
    width = 800
    header_h = 60
    row_h = 50
    padding = 40
    
    height = padding*2 + header_h + (len(rows) * row_h) + 60
    
    # Dark background colors matching Fragment/Telegram theme
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
    
    # Draw Title
    draw.text((padding, padding), title, fill=text_primary, font=font_title)
    
    # Draw Card Background
    card_y = padding + 60
    card_h = header_h + (len(rows) * row_h)
    draw.rounded_rectangle([padding, card_y, width-padding, card_y+card_h], radius=15, fill=card_color)
    
    # Draw Headers
    cols_x = [padding + 20, padding + 120, width - 250] # X positions for columns
    for i, h in enumerate(headers):
        draw.text((cols_x[i], card_y + 15), h, fill=text_secondary, font=font_header)
        
    # Draw Line under header
    draw.line([padding, card_y + header_h, width-padding, card_y + header_h], fill="#3A4150", width=2)
    
    # Draw Rows
    y_offset = card_y + header_h
    for row in rows:
        draw.text((cols_x[0], y_offset + 15), str(row[0]), fill=text_secondary, font=font_row)
        draw.text((cols_x[1], y_offset + 15), str(row[1]), fill=accent_color, font=font_row) # Telegram blue
        draw.text((cols_x[2], y_offset + 15), str(row[2]), fill=text_primary, font=font_row)
        
        # Line separator for rows
        draw.line([padding, y_offset + row_h, width-padding, y_offset + row_h], fill="#3A4150", width=1)
        y_offset += row_h
        
    # Draw ANYSNAP Branding
    draw.text((width/2, height - 30), "Powered by ANYSNAP", fill=text_secondary, font=font_watermark, anchor="mm")
    
    # Save to memory buffer
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf