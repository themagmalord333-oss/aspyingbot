import io
import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size, bold=False):
    # Ubuntu default fonts for clean UI
    fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf" if bold else "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
    ]
    for f in fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
    return ImageFont.load_default()

def create_market_image(title, col_name, items):
    width = 900
    padding = 40
    title_area = 80
    header_h = 70
    row_h = 65
    
    height = padding*2 + title_area + header_h + (len(items) * row_h)
    
    # Exact Fragment UI Colors
    bg_color = '#17191F'
    card_color = '#232834'
    text_white = '#FFFFFF'
    text_grey = '#7E8C99'
    text_blue = '#4CA0E3'
    line_color = '#2D3242'
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(36, bold=True)
    font_header = get_font(22, bold=True)
    font_row = get_font(22, bold=False)
    font_bold = get_font(22, bold=True)
    
    # Title (Centered)
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((width - title_w) / 2, padding), title, fill=text_white, font=font_title)
    
    # Table Card
    card_y = padding + title_area
    card_h = header_h + (len(items) * row_h)
    draw.rounded_rectangle([padding, card_y, width-padding, card_y+card_h], radius=16, fill=card_color)
    
    # Columns setup
    cols_x = [padding + 30, padding + 120, padding + 420, padding + 620, padding + 720]
    headers = ["#", col_name, "Auction end", "Bids", "Price"]
    
    for i, h in enumerate(headers):
        draw.text((cols_x[i], card_y + 25), h, fill=text_grey, font=font_header)
        
    y_offset = card_y + header_h
    for idx, item in enumerate(items):
        # Row Divider
        draw.line([padding, y_offset, width-padding, y_offset], fill=line_color, width=2)
        
        # Row Data
        draw.text((cols_x[0], y_offset + 20), str(idx+1), fill=text_grey, font=font_row)
        draw.text((cols_x[1], y_offset + 20), str(item.get('name', 'N/A')), fill=text_blue, font=font_row)
        draw.text((cols_x[2], y_offset + 20), str(item.get('ends', '-')), fill=text_grey, font=font_row)
        draw.text((cols_x[3], y_offset + 20), str(item.get('bids', '-')), fill=text_grey, font=font_row)
        draw.text((cols_x[4], y_offset + 20), str(item.get('price', '-')), fill=text_blue, font=font_bold)
        
        y_offset += row_h
        
    # Branding completely removed
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf