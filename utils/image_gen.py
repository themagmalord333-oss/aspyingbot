import io
import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size, bold=False):
    # Pydroid 3 (Android) and Linux font paths
    fonts = [
        "/system/fonts/Roboto-Bold.ttf" if bold else "/system/fonts/Roboto-Regular.ttf",
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

# --- COLORS ---
BG_COLOR = '#17191F'
CARD_COLOR = '#232834'
TEXT_WHITE = '#FFFFFF'
TEXT_GREY = '#7E8C99'
TEXT_BLUE = '#4CA0E3'
TEXT_RED = '#E5575F'
LINE_COLOR = '#2D3242'

def create_market_image(title, col_name, items):
    """Generates lists for Auctions, Domains, Numbers, Trending"""
    width = 900
    padding = 40
    header_h = 70
    row_h = 65
    title_area = 100

    height = padding*2 + title_area + header_h + (len(items) * row_h)
    
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = get_font(36, bold=True)
    font_header = get_font(20, bold=True)
    font_row = get_font(20, bold=False)

    # Title
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, padding), title, fill=TEXT_WHITE, font=font_title)

    # Card background
    card_y = padding + title_area
    card_h = header_h + (len(items) * row_h)
    draw.rounded_rectangle([padding, card_y, width-padding, card_y+card_h], radius=16, fill=CARD_COLOR)

    # Columns
    cols_x = [padding + 30, padding + 120, padding + 400, padding + 580, padding + 700]
    headers = ["#", col_name, "Auction end" if "Auction" in title else "Ends", "Bids", "Price"]

    for i, h in enumerate(headers):
        draw.text((cols_x[i], card_y + 25), h, fill=TEXT_GREY, font=font_header)

    y_offset = card_y + header_h
    for idx, item in enumerate(items):
        draw.line([padding, y_offset, width-padding, y_offset], fill=LINE_COLOR, width=2)
        
        draw.text((cols_x[0], y_offset + 20), str(idx+1), fill=TEXT_GREY, font=font_row)
        
        draw.text((cols_x[1], y_offset + 20), str(item.get('name', 'N/A')), fill=TEXT_WHITE if "GRAM" in str(item.get('name', '')) else TEXT_BLUE, font=font_row)
        draw.text((cols_x[2], y_offset + 20), str(item.get('ends', '-')), fill=TEXT_GREY, font=font_row)
        draw.text((cols_x[3], y_offset + 20), str(item.get('bids', '-')), fill=TEXT_GREY, font=font_row)
        
        price = str(item.get('price', '-'))
        draw.text((cols_x[4], y_offset + 20), price.replace(" GRAM", ""), fill=TEXT_BLUE, font=get_font(20, bold=True))
        
        if "GRAM" in price:
             draw.text((cols_x[4] + 90, y_offset + 20), "GRAM", fill=TEXT_GREY, font=get_font(16, bold=True))

        y_offset += row_h

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def create_status_image(username, status_text):
    """Generates the single username search result image (e.g., Banned)"""
    width = 800
    height = 350
    
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_main = get_font(48, bold=True)
    font_sub = get_font(22, bold=False)
    
    # Username Header
    draw.text((50, 50), f"{username}.t.me", fill=TEXT_WHITE, font=font_main)
    draw.text((50, 120), f"@{username} • t.me/{username}", fill=TEXT_GREY, font=font_sub)
    
    # Status Card
    draw.rounded_rectangle([50, 180, width-50, 300], radius=16, fill=CARD_COLOR)
    draw.text((80, 225), status_text, fill=TEXT_GREY, font=font_sub)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def create_history_image(username, history_items):
    """Generates the Ownership History image"""
    width = 800
    row_h = 70
    height = 200 + (len(history_items) * row_h)
    
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(32, bold=True)
    font_row = get_font(20, bold=False)
    
    # Title
    title = "Ownership History"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, 40), title, fill=TEXT_WHITE, font=font_title)
    
    # Card
    draw.rounded_rectangle([50, 120, width-50, height-40], radius=16, fill=CARD_COLOR)
    
    draw.text((200, 145), "Date", fill=TEXT_GREY, font=get_font(20, bold=True))
    draw.text((550, 145), "Buyer", fill=TEXT_GREY, font=get_font(20, bold=True))
    
    y_offset = 190
    for item in history_items:
        draw.line([50, y_offset, width-50, y_offset], fill=LINE_COLOR, width=2)
        # Assuming item is a tuple: (date, buyer) or single string to parse
        if isinstance(item, tuple):
            date, buyer = item
        else:
            parts = item.replace("• ", "").split(":")
            date = parts[0].strip() if len(parts) > 0 else "-"
            buyer = parts[1].strip() if len(parts) > 1 else "-"
            
        draw.text((100, y_offset + 25), date, fill=TEXT_GREY, font=font_row)
        draw.text((500, y_offset + 25), buyer, fill=TEXT_BLUE, font=font_row)
        y_offset += row_h

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def create_similar_image(username, similar_items):
    """Generates the Similar Usernames image"""
    width = 600
    row_h = 70
    height = 200 + (len(similar_items) * row_h)
    
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(36, bold=True)
    font_sub = get_font(20, bold=False)
    
    # Header
    title = f"@{username}"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, 40), title, fill=TEXT_WHITE, font=font_title)
    
    sub = f"{len(similar_items)} similar usernames found"
    bbox_sub = draw.textbbox((0, 0), sub, font=font_sub)
    draw.text(((width - (bbox_sub[2]-bbox_sub[0])) / 2, 90), sub, fill=TEXT_GREY, font=font_sub)
    
    # List Cards
    y_offset = 150
    for item in similar_items:
        draw.rounded_rectangle([40, y_offset, width-40, y_offset + row_h - 10], radius=12, fill=CARD_COLOR)
        # Red Dot
        draw.ellipse([60, y_offset + 25, 70, y_offset + 35], fill=TEXT_RED)
        draw.text((90, y_offset + 18), item, fill=TEXT_WHITE, font=get_font(22, bold=True))
        draw.text((width - 150, y_offset + 20), "Non-NFT", fill=TEXT_RED, font=font_sub)
        y_offset += row_h
        
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf