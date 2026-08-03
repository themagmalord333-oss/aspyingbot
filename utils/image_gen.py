import io
import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size, bold=False):
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

# --- NEW PRO UI COLORS (Matching the exactly provided screenshots) ---
BG_COLOR = '#161C24'        # Dark Outer Background
CARD_COLOR = '#212B36'      # Main Box Background
HEADER_BG = '#2C3A47'       # Table Header Background
TEXT_WHITE = '#FFFFFF'      # Main Headers & Title
TEXT_GREY = '#8C9EAE'       # Secondary Text (Ends, Bids)
TEXT_BLUE = '#52A8E5'       # Price Text Color
TEXT_GRAM = '#435565'       # Dark grey 'GRAM' text
LINE_COLOR = '#161C24'      # Row separator (matches BG for "gap" effect)


def draw_ton_icon(draw, x, y, size=24):
    draw.ellipse([x, y, x+size, y+size], fill="#52A8E5")
    dx, dy = x + size/2, y + size/2
    s = size * 0.22
    draw.polygon([(dx, dy-s), (dx+s, dy), (dx, dy+s), (dx-s, dy)], fill="#FFFFFF")


def truncate_wallet(text):
    if len(text) > 20 and not text.endswith(".ton"):
        return f"{text[:9]}...{text[-6:]}"
    return text


def create_market_image(title, col_name, items):
    """Generates Pixel-Perfect dynamic tables mapping exactly to the reference images."""
    display_items = items[:5] # Force exactly 5 rows to match layout

    width = 850
    padding = 30
    header_h = 65
    row_h = 65
    title_area = 80

    height = padding*2 + title_area + header_h + (len(display_items) * row_h)

    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = get_font(34, bold=True)
    font_header = get_font(18, bold=True)
    font_row = get_font(18, bold=False)
    font_price = get_font(18, bold=True)
    font_gram = get_font(14, bold=True)

    # 1. Main Centered Title
    draw.text((width / 2, padding + 15), title, fill=TEXT_WHITE, font=font_title, anchor="mm")

    card_y = padding + title_area
    card_h = header_h + (len(display_items) * row_h)

    # 2. Main Containers
    draw.rounded_rectangle([padding, card_y, width-padding, card_y+card_h], radius=16, fill=CARD_COLOR)
    draw.rounded_rectangle([padding, card_y, width-padding, card_y+header_h], radius=16, fill=HEADER_BG)
    draw.rectangle([padding, card_y+header_h-16, width-padding, card_y+header_h], fill=HEADER_BG)

    # 3. Dynamic Matrix Coordinates setup
    is_trending = "Trending" in title
    is_number = "Number" in title

    if is_trending:
        headers = ["#", "Username", "Bids", "Price", "Ends"]
        cols_x = [padding + 30, padding + 120, padding + 390, padding + 520, padding + 700]
    elif is_number:
        headers = ["#", "Number", "Auction end", "Price"]
        cols_x = [padding + 30, padding + 120, padding + 420, padding + 630]
    else:
        headers = ["#", col_name, "Auction end", "Bids", "Price"]
        cols_x = [padding + 30, padding + 120, padding + 330, padding + 530, padding + 640]

    # GRAM vertical alignment constant
    gram_x = width - padding - 65

    def draw_vcentered(x, y_start, y_end, text, font, fill):
        t_bbox = draw.textbbox((0, 0), text, font=font)
        y_pos = y_start + ((y_end - y_start) - (t_bbox[3] - t_bbox[1])) / 2 - 4
        draw.text((x, y_pos), text, fill=fill, font=font)

    # 4. Draw Header
    for i, h in enumerate(headers):
        draw_vcentered(cols_x[i], card_y, card_y+header_h, h, font_header, TEXT_GREY)

    # 5. Draw Exact Aligned Rows
    y_offset = card_y + header_h
    for idx, item in enumerate(display_items):
        # The exact gap divider
        draw.line([padding, y_offset, width-padding, y_offset], fill=LINE_COLOR, width=2)

        draw_vcentered(cols_x[0], y_offset, y_offset+row_h, str(idx+1), font_row, TEXT_GREY)

        name_val = str(item.get('name', 'N/A'))
        ends_val = str(item.get('ends', '-'))
        bids_val = str(item.get('bids', '0'))
        price_val = str(item.get('price', '-')).replace(" GRAM", "")

        if is_trending:
            draw_vcentered(cols_x[1], y_offset, y_offset+row_h, name_val, font_row, TEXT_BLUE)
            draw_vcentered(cols_x[2], y_offset, y_offset+row_h, bids_val, font_row, TEXT_GREY)
            draw_vcentered(cols_x[3], y_offset, y_offset+row_h, price_val, font_price, TEXT_BLUE)
            draw_vcentered(cols_x[4], y_offset, y_offset+row_h, ends_val, font_row, TEXT_GREY)

        elif is_number:
            draw_vcentered(cols_x[1], y_offset, y_offset+row_h, name_val, font_row, TEXT_GREY)
            draw_vcentered(cols_x[2], y_offset, y_offset+row_h, ends_val, font_row, TEXT_GREY)
            draw_vcentered(cols_x[3], y_offset, y_offset+row_h, price_val, font_price, TEXT_BLUE)
            if price_val != "-":
                draw_vcentered(gram_x, y_offset, y_offset+row_h, "GRAM", font_gram, TEXT_GRAM)

        else:
            draw_vcentered(cols_x[1], y_offset, y_offset+row_h, name_val, font_row, TEXT_GREY)
            draw_vcentered(cols_x[2], y_offset, y_offset+row_h, ends_val, font_row, TEXT_GREY)
            draw_vcentered(cols_x[3], y_offset, y_offset+row_h, bids_val, font_row, TEXT_GREY)
            draw_vcentered(cols_x[4], y_offset, y_offset+row_h, price_val, font_price, TEXT_BLUE)
            if price_val != "-":
                draw_vcentered(gram_x, y_offset, y_offset+row_h, "GRAM", font_gram, TEXT_GRAM)

        y_offset += row_h

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def create_status_image(username, data):
    width = 850
    height = 320

    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_main = get_font(48, bold=True)
    font_sub = get_font(22, bold=False)
    font_small = get_font(18, bold=False)
    font_val = get_font(32, bold=True)

    status_lower = data.get("status", "Unknown").lower()

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

    if "auction" in status_lower:
        draw.rounded_rectangle([badge_x, 45, badge_x + 130, 85], radius=10, fill="#2C3A47")
        draw.text((badge_x + 15, 55), "On Auction", fill="#E59A3D", font=get_font(18, bold=True))
        if data.get("ends_in"):
            b2_x = badge_x + 145
            draw.rounded_rectangle([b2_x, 45, b2_x + 160, 85], radius=10, fill="#2C3A47")
            draw.text((b2_x + 15, 55), f"Ends in {data['ends_in']}", fill="#E59A3D", font=get_font(18, bold=True))

    elif "sold" in status_lower:
        draw.rounded_rectangle([badge_x, 45, badge_x + 80, 85], radius=10, fill="#2C3A47")
        draw.text((badge_x + 15, 55), "Sold", fill="#E5575F", font=get_font(18, bold=True))

    elif "banned" in status_lower:
        draw.rounded_rectangle([badge_x, 45, badge_x + 100, 85], radius=10, fill=CARD_COLOR)
        draw.text((badge_x + 15, 55), "Banned", fill=TEXT_WHITE, font=get_font(18, bold=True))

    card_y = 150
    draw.rounded_rectangle([50, card_y, width-50, card_y + 130], radius=16, fill=CARD_COLOR)

    if "auction" in status_lower:
        draw.text((80, card_y + 20), "Highest Bid", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, 80, card_y + 55, size=28)
        draw.text((120, card_y + 50), data.get('highest_bid', '0'), fill=TEXT_WHITE, font=font_val)
        draw.text((120, card_y + 90), data.get('usd_highest', ''), fill="#41C066", font=font_small)

        col2_x = 350
        draw.text((col2_x, card_y + 20), "Bid Step", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, col2_x, card_y + 55, size=28)
        draw.text((col2_x + 40, card_y + 50), data.get('bid_step', '0'), fill=TEXT_WHITE, font=font_val)

        col3_x = 600
        draw.text((col3_x, card_y + 20), "Minimum Bid", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, col3_x, card_y + 55, size=28)
        draw.text((col3_x + 40, card_y + 50), data.get('min_bid', '0'), fill=TEXT_WHITE, font=font_val)
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
    width = 800
    row_h = 65
    card_top = 110
    card_bottom = card_top + (len(history_items) * row_h) + row_h
    height = card_bottom + 35

    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = get_font(34, bold=True)
    font_row = get_font(20, bold=False)
    font_header = get_font(20, bold=True)

    draw.text((width / 2, 55), "Ownership History", fill=TEXT_WHITE, font=font_title, anchor="mm")

    card_left = 40
    card_right = width - 40
    center_x = width / 2
    left_center = card_left + (center_x - card_left) / 2
    right_center = center_x + (card_right - center_x) / 2

    draw.rounded_rectangle([card_left, card_top, card_right, card_bottom], radius=16, fill=CARD_COLOR)
    draw.rounded_rectangle([card_left, card_top, card_right, card_top + row_h], radius=16, fill=HEADER_BG)
    draw.rectangle([card_left, card_top + row_h - 16, card_right, card_top + row_h], fill=HEADER_BG)
    draw.line([center_x, card_top, center_x, card_bottom], fill=LINE_COLOR, width=2)

    h_cy = card_top + (row_h / 2)
    draw.text((left_center, h_cy), "Date", fill=TEXT_GREY, font=font_header, anchor="mm")
    draw.text((right_center, h_cy), "Buyer", fill=TEXT_GREY, font=font_header, anchor="mm")

    y_offset = card_top + row_h
    for item in history_items:
        draw.line([card_left, y_offset, card_right, y_offset], fill=LINE_COLOR, width=2)
        if isinstance(item, tuple):
            date, buyer = item
        else:
            date, buyer = "-", "-"

        buyer = truncate_wallet(buyer)

        r_cy = y_offset + (row_h / 2)
        draw.text((left_center, r_cy), date, fill=TEXT_GREY, font=font_row, anchor="mm")
        draw.text((right_center, r_cy), buyer, fill=TEXT_BLUE, font=font_row, anchor="mm")

        y_offset += row_h

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def create_similar_image(username, similar_items):
    width = 650
    row_h = 65
    height = 180 + (len(similar_items) * row_h)

    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    font_title = get_font(34, bold=True)
    font_sub = get_font(18, bold=False)

    draw.text((width / 2, 45), f"@{username}", fill=TEXT_WHITE, font=font_title, anchor="mm")
    draw.text((width / 2, 90), f"{len(similar_items)} search results found", fill=TEXT_GREY, font=font_sub, anchor="mm")

    y_offset = 135
    for item in similar_items:
        draw.rounded_rectangle([35, y_offset, width-35, y_offset + row_h - 10], radius=12, fill=CARD_COLOR)
        row_cy = y_offset + (row_h - 10) / 2

        if item.get("is_nft"):
            draw.ellipse([55, y_offset + 22, 65, y_offset + 32], fill=TEXT_BLUE)
            draw.text((80, row_cy), item["name"], fill=TEXT_WHITE, font=get_font(20, bold=True), anchor="lm")

            price = item.get("price", "").replace(" TON", "")
            status_text = item.get("status", "")

            if status_text == "Sold":
                status_color = "#8C9EAE" 
            elif status_text == "Available":
                status_color = "#41C066" 
            elif status_text == "On Auction":
                status_color = "#E59A3D" 
            else:
                status_color = TEXT_GREY

            if price and price != "-":
                draw_ton_icon(draw, width - 180, row_cy - 11, size=22)
                draw.text((width - 150, row_cy), price, fill=TEXT_BLUE, font=get_font(20, bold=True), anchor="lm")
                draw.text((width - 290, row_cy), status_text, fill=status_color, font=get_font(16, bold=False), anchor="lm")
            else:
                draw.text((width - 160, row_cy), status_text, fill=status_color, font=font_sub, anchor="lm")
        else:
            draw.ellipse([55, y_offset + 22, 65, y_offset + 32], fill=TEXT_RED)
            draw.text((80, row_cy), item["name"], fill=TEXT_WHITE, font=get_font(20, bold=True), anchor="lm")
            draw.text((width - 140, row_cy), item.get("status", "Non-NFT"), fill=TEXT_RED, font=font_sub, anchor="lm")

        y_offset += row_h

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def create_balance_image(target_name, ton_bal, usd_bal):
    width = 600
    height = 290
    bg_color = '#161C24' 

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    font_title = get_font(30, bold=True)
    font_val = get_font(34, bold=True)
    font_label = get_font(26, bold=True)

    display_name = target_name.replace('.t.me', '').replace('.ton', '')
    display_name = truncate_wallet(display_name)

    draw.text((width / 2, 40), f"@{display_name}'s Balance", fill=TEXT_WHITE, font=font_title, anchor="mm")

    pill1_y = 85
    draw.rounded_rectangle([35, pill1_y, width-35, pill1_y + 75], radius=22, fill="#212B36")
    draw.rounded_rectangle([45, pill1_y + 9, 220, pill1_y + 66], radius=18, fill="#102B3F")
    draw_ton_icon(draw, 60, pill1_y + 24, size=26)
    draw.text((98, pill1_y + 37), "GRAM", fill="#52A8E5", font=font_label, anchor="lm")

    val1 = f"{ton_bal:,.2f}"
    draw.text((width - 55, pill1_y + 37), val1, fill=TEXT_GREY, font=font_val, anchor="rm")

    pill2_y = 180
    draw.rounded_rectangle([35, pill2_y, width-35, pill2_y + 75], radius=22, fill="#212B36")
    draw.rounded_rectangle([45, pill2_y + 9, 220, pill2_y + 66], radius=18, fill="#0E2D17")
    draw.ellipse([60, pill2_y + 23, 88, pill2_y + 51], fill="#34C759")
    draw.text((74, pill2_y + 36), "$", fill="#000000", font=get_font(22, bold=True), anchor="mm")
    draw.text((105, pill2_y + 37), "USD", fill="#34C759", font=font_label, anchor="lm")

    val2 = f"${usd_bal:,.2f}"
    draw.text((width - 55, pill2_y + 37), val2, fill=TEXT_GREY, font=font_val, anchor="rm")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


# ==========================================
# NEW: Floor Prices 3-Box Generator (Widened Boxes to fix overlap)
# ==========================================
def create_floor_image(data):
    width, height = 980, 320
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(36, bold=True)
    font_box_title = get_font(24, bold=True)
    font_price = get_font(40, bold=True)
    font_usd = get_font(20, bold=True)
    font_icon = get_font(45, bold=True)
    font_icon_small = get_font(22, bold=True)
        
    draw.text((width/2, 45), "Floor Prices", fill=TEXT_WHITE, font=font_title, anchor="mm")
    
    # BOX SIZES INCREASED SO PRICE & USD DON'T OVERLAP
    box_w, box_h = 290, 150
    spacing = 25
    start_x = (width - ((box_w * 3) + (spacing * 2))) // 2
    start_y = 110
    
    boxes = [
        {"icon": "#", "is_small": False, "t1": "Number", "t2": "Floor Price", "ton": data["number"]["ton"], "usd": data["number"]["usd"]},
        {"icon": "@4c", "is_small": True, "t1": "4 Character", "t2": "Floor Price", "ton": data["char4"]["ton"], "usd": data["char4"]["usd"]},
        {"icon": "@", "is_small": False, "t1": "Username", "t2": "Floor Price", "ton": data["user"]["ton"], "usd": data["user"]["usd"]}
    ]
    
    for i, box in enumerate(boxes):
        x = start_x + (i * (box_w + spacing))
        y = start_y
        
        draw.rounded_rectangle([x, y, x + box_w, y + box_h], radius=20, fill=CARD_COLOR)
        
        ix, iy = x + 20, y + 20
        draw.rounded_rectangle([ix, iy, ix + 55, iy + 55], radius=15, fill=BG_COLOR)
        
        if box["is_small"]:
            draw.text((ix + 27, iy + 27), box["icon"], fill=TEXT_BLUE, font=font_icon_small, anchor="mm")
        else:
            draw.text((ix + 27, iy + 27), box["icon"], fill=TEXT_BLUE, font=font_icon, anchor="mm")
        
        draw.text((x + 90, y + 22), box["t1"], fill=TEXT_WHITE, font=font_box_title)
        draw.text((x + 90, y + 52), box["t2"], fill=TEXT_WHITE, font=font_box_title)
        
        draw_ton_icon(draw, x + 20, y + 90, size=32)
        
        draw.text((x + 65, y + 84), box["ton"], fill=TEXT_WHITE, font=font_price)
        
        try:
            t_bbox = draw.textbbox((0, 0), box["ton"], font=font_price)
            ton_w = t_bbox[2] - t_bbox[0]
        except:
            ton_w = len(box["ton"]) * 20
            
        draw.text((x + 65 + ton_w + 10, y + 104), box["usd"], fill=TEXT_GREY, font=font_usd)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf