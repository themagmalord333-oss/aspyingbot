def draw_ton_icon(draw, x, y, size=24):
    """Custom function to draw the TON logo."""
    draw.ellipse([x, y, x+size, y+size], fill="#4CA0E3")
    dx, dy = x + size/2, y + size/2
    s = size * 0.22
    draw.polygon([(dx, dy-s), (dx+s, dy), (dx, dy+s), (dx-s, dy)], fill="#FFFFFF")

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
    
    # 1. Username Header
    name_text = f"{username}.t.me"
    bbox = draw.textbbox((0, 0), name_text, font=font_main)
    name_w = bbox[2] - bbox[0]
    draw.text((50, 40), name_text, fill=TEXT_WHITE, font=font_main)
    
    # 2. Subtitle
    draw.text((50, 105), f"@{username} • t.me/{username}", fill=TEXT_GREY, font=font_sub)
    
    # 3. Badges Logic
    status = data.get("status", "Unknown")
    badge_x = 50 + name_w + 20
    
    if "Auction" in status:
        # On Auction Badge
        draw.rounded_rectangle([badge_x, 45, badge_x + 130, 85], radius=10, fill="#3A2A1A")
        draw.text((badge_x + 15, 55), "On Auction", fill="#E59A3D", font=get_font(18, bold=True))
        
        # Ends In Badge
        if data.get("ends_in"):
            b2_x = badge_x + 145
            draw.rounded_rectangle([b2_x, 45, b2_x + 160, 85], radius=10, fill="#3A2A1A")
            draw.text((b2_x + 15, 55), f"Ends in {data['ends_in']}", fill="#E59A3D", font=get_font(18, bold=True))
            
    elif "Banned" in status:
        draw.rounded_rectangle([badge_x, 45, badge_x + 100, 85], radius=10, fill="#1C1E23")
        draw.text((badge_x + 15, 55), "Banned", fill="#FFFFFF", font=get_font(18, bold=True))
    
    # 4. Main Card Background
    card_y = 150
    draw.rounded_rectangle([50, card_y, width-50, card_y + 130], radius=16, fill=CARD_COLOR)
    
    # 5. Card Content Conditional Rendering
    if "Auction" in status:
        # Column 1: Highest Bid
        draw.text((80, card_y + 20), "Highest Bid", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, 80, card_y + 55, size=28)
        draw.text((120, card_y + 50), data.get('highest_bid', '-'), fill=TEXT_WHITE, font=font_val)
        draw.text((120, card_y + 90), data.get('usd_highest', ''), fill="#41C066", font=font_small)
        
        # Column 2: Bid Step
        col2_x = 350
        draw.text((col2_x, card_y + 20), "Bid Step", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, col2_x, card_y + 55, size=28)
        draw.text((col2_x + 40, card_y + 50), data.get('bid_step', '-'), fill=TEXT_WHITE, font=font_val)
        
        # Column 3: Minimum Bid
        col3_x = 600
        draw.text((col3_x, card_y + 20), "Minimum Bid", fill=TEXT_GREY, font=font_small)
        draw_ton_icon(draw, col3_x, card_y + 55, size=28)
        draw.text((col3_x + 40, card_y + 50), data.get('min_bid', '-'), fill=TEXT_WHITE, font=font_val)
        draw.text((col3_x + 40, card_y + 90), data.get('usd_min', ''), fill="#41C066", font=font_small)

    else:
        # Banned, Available, Sold layouts (Simple text inside card)
        info = data.get("info_text", f"This username is {status}.")
        draw.text((80, card_y + 50), info, fill=TEXT_GREY, font=font_sub)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf
