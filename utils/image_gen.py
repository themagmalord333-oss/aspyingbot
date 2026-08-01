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


def draw_ton_icon(draw, x, y, size=24):
    """Custom function to draw the TON logo."""
    draw.ellipse([x, y, x+size, y+size], fill="#4CA0E3")
    dx, dy = x + size/2, y + size/2
    s = size * 0.22
    draw.polygon([(dx, dy-s), (dx+s, dy), (dx, dy+s), (dx-s, dy)], fill="#FFFFFF")


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

    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, padding), title, fill=TEXT_WHITE, font=font_title)

    card_y = padding + title_area
    card_h = header_h + (len(items) * row_h)
    draw.rounded_rectangle([padding, card_y, width-padding, card_y+card_h], radius=16, fill=CARD_COLOR)

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


def create_status_image(username, data):
    """Generates the detailed single username search result image"""
    width = 850
    height = 320
    
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_main = get_font(48, bold=True)
    font_sub = get_font(22, bold=False)
    font_small = get_font(18, bold=False)
    font_val = get_font(32, bold=True)
    
    status_lower = data.get("status", "Unknown").lower()
    
    # Left Yellow Accent Line for Auctions & Red for Sold
    if "auction" in status_lower:
        draw.rectangle([0, 0, 8, height], fill="#E59A3D")
    elif "sold" in status_lower:
        draw.rectangle([0, 0, 8, height], fill="#E5575F")
    
    name_text = f"{username}.t.me"
    bbox = draw.textbbox((0, 0), name_text, font=font_main)
    name_w = bbox[2] - bbox[0]
    draw.text((50, 40), name_text, fill=TEXT_WHITE, font=font_main)
    
    draw.text((50, 105), f"@{username} • t.me/{username}", fill=TEXT_GREY, font=font_sub)
    
    badge_x = 50 + name_w + 20
    
    # Dynamic Badges
    if "auction" in status_lower:
        draw.rounded_rectangle([badge_x, 45, badge_x + 130, 85], radius=10, fill="#3A2A1A")
        draw.text((badge_x + 15, 55), "On Auction", fill="#E59A3D", font=get_font(18, bold=True))
        if data.get("ends_in"):
            b2_x = badge_x + 145
            draw.rounded_rectangle([b2_x, 45, b2_x + 160, 85], radius=10, fill="#3A2A1A")
            draw.text((b2_x + 15, 55), f"Ends in {data['ends_in']}", fill="#E59A3D", font=get_font(18, bold=True))
            
    elif "sold" in status_lower:
        draw.rounded_rectangle([badge_x, 45, badge_x + 80, 85], radius=10, fill="#3D1C20")
        draw.text((badge_x + 15, 55), "Sold", fill="#E5575F", font=get_font(18, bold=True))
        
    elif "banned" in status_lower:
        draw.rounded_rectangle([badge_x, 45, badge_x + 100, 85], radius=10, fill="#1C1E23")
        draw.text((badge_x + 15, 55), "Banned", fill="#FFFFFF", font=get_font(18, bold=True))
    
    # Main Card
    card_y = 150
    draw.rounded_rectangle([50, card_y, width-50, card_y + 130], radius=16, fill=CARD_COLOR)
    
    if "auction" in status_lower:
        draw.text((80, card_y + 20), "Highest Bid", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, 80, card_y + 55, size=28)
        draw.text((120, card_y + 50), data.get('highest_bid', '-'), fill=TEXT_WHITE, font=font_val)
        draw.text((120, card_y + 90), data.get('usd_highest', ''), fill="#41C066", font=font_small)
        
        col2_x = 350
        draw.text((col2_x, card_y + 20), "Bid Step", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, col2_x, card_y + 55, size=28)
        draw.text((col2_x + 40, card_y + 50), data.get('bid_step', '-'), fill=TEXT_WHITE, font=font_val)
        
        col3_x = 600
        draw.text((col3_x, card_y + 20), "Minimum Bid", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, col3_x, card_y + 55, size=28)
        draw.text((col3_x + 40, card_y + 50), data.get('min_bid', '-'), fill=TEXT_WHITE, font=font_val)
        draw.text((col3_x + 40, card_y + 90), data.get('usd_min', ''), fill="#41C066", font=font_small)

    elif "sold" in status_lower:
        draw.text((80, card_y + 20), "Sale Price", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, 80, card_y + 55, size=28)
        draw.text((120, card_y + 50), data.get('sold_price', '-'), fill=TEXT_WHITE, font=font_val)
        
    else:
        info = data.get("info_text", f"This username is {data.get('status', 'Unknown')}.")
        draw.text((80, card_y + 50), info, fill=TEXT_GREY, font=font_sub)
    
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
    
    title = "Ownership History"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, 40), title, fill=TEXT_WHITE, font=font_title)
    
    draw.rounded_rectangle([50, 120, width-50, height-40], radius=16, fill=CARD_COLOR)
    
    draw.text((200, 145), "Date", fill=TEXT_GREY, font=get_font(20, bold=True))
    draw.text((550, 145), "Buyer", fill=TEXT_GREY, font=get_font(20, bold=True))
    
    y_offset = 190
    for item in history_items:
        draw.line([50, y_offset, width-50, y_offset], fill=LINE_COLOR, width=2)
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
    """Generates the Similar Usernames image with Live Prices/Status"""
    width = 650
    row_h = 70
    height = 200 + (len(similar_items) * row_h)
    
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(36, bold=True)
    font_sub = get_font(20, bold=False)
    
    title = f"@{username}"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, 40), title, fill=TEXT_WHITE, font=font_title)
    
    sub = f"{len(similar_items)} search results found"
    bbox_sub = draw.textbbox((0, 0), sub, font=font_sub)
    draw.text(((width - (bbox_sub[2]-bbox_sub[0])) / 2, 90), sub, fill=TEXT_GREY, font=font_sub)
    
    y_offset = 150
    for item in similar_items:
        draw.rounded_rectangle([40, y_offset, width-40, y_offset + row_h - 10], radius=12, fill=CARD_COLOR)
        
        # Determine NFT vs Non-NFT UI
        if item.get("is_nft"):
            draw.ellipse([60, y_offset + 25, 70, y_offset + 35], fill=TEXT_BLUE) # Blue dot
            draw.text((90, y_offset + 18), item["name"], fill=TEXT_WHITE, font=get_font(22, bold=True))
            
            # Show Price if available
            price = item.get("price", "").replace(" TON", "")
            status_text = item.get("status", "")
            
            if price and price != "-":
                # Draw Price with TON icon
                draw_ton_icon(draw, width - 200, y_offset + 20, size=22)
                draw.text((width - 170, y_offset + 18), price, fill=TEXT_BLUE, font=get_font(22, bold=True))
                # Draw Status (Sold/Auction) next to it
                draw.text((width - 310, y_offset + 20), status_text, fill=TEXT_GREY, font=get_font(18, bold=False))
            else:
                draw.text((width - 180, y_offset + 20), status_text, fill=TEXT_BLUE, font=font_sub)
        else:
            draw.ellipse([60, y_offset + 25, 70, y_offset + 35], fill=TEXT_RED) # Red dot
            draw.text((90, y_offset + 18), item["name"], fill=TEXT_WHITE, font=get_font(22, bold=True))
            draw.text((width - 150, y_offset + 20), item.get("status", "Non-NFT"), fill=TEXT_RED, font=font_sub)
            
        y_offset += row_h
        
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def create_balance_image(target_name, ton_bal, usd_bal):
    """Generates the dual-pill Balance design as per the image"""
    width = 600
    height = 300
    bg_color = '#0F0F0F' 
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(32, bold=True)
    font_val = get_font(36, bold=True)
    font_label = get_font(28, bold=True)
    
    display_name = target_name.replace('.t.me', '').replace('.ton', '')
    title = f"@{display_name}'s Balance"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, 25), title, fill="#FFFFFF", font=font_title)
    
    # 1st Pill (GRAM)
    pill1_y = 90
    draw.rounded_rectangle([40, pill1_y, width-40, pill1_y + 80], radius=25, fill="#16181C")
    draw.rounded_rectangle([50, pill1_y + 10, 230, pill1_y + 70], radius=20, fill="#102B3F")
    draw_ton_icon(draw, 65, pill1_y + 25, size=28)
    draw.text((105, pill1_y + 22), "GRAM", fill="#2896D2", font=font_label)
    
    val1 = f"{ton_bal:,.2f}"
    bbox1 = draw.textbbox((0,0), val1, font=font_val)
    draw.text((width - 60 - (bbox1[2]-bbox1[0]), pill1_y + 18), val1, fill="#68717A", font=font_val)
    
    # 2nd Pill (USD)
    pill2_y = 190
    draw.rounded_rectangle([40, pill2_y, width-40, pill2_y + 80], radius=25, fill="#16181C")
    draw.rounded_rectangle([50, pill2_y + 10, 230, pill2_y + 70], radius=20, fill="#0E2D17")
    draw.ellipse([65, pill2_y + 24, 95, pill2_y + 54], fill="#34C759")
    draw.text((74, pill2_y + 25), "$", fill="#000000", font=get_font(24, bold=True))
    draw.text((115, pill2_y + 22), "USD", fill="#34C759", font=font_label)
    
    val2 = f"${usd_bal:,.2f}"
    bbox2 = draw.textbbox((0,0), val2, font=font_val)
    draw.text((width - 60 - (bbox2[2]-bbox2[0]), pill2_y + 18), val2, fill="#68717A", font=font_val)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf
