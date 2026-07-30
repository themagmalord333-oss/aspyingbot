from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from fragment.scraper import *
from utils.image_gen import create_table_image  # <-- Naya Import

router = Router()

# ... (Upar ke functions cmd_fragment, cmd_similar, cmd_history waise hi rahenge) ...

@router.message(Command("auctions", "domains", "numbers", "trending", "floor"))
async def cmd_markets(message: Message):
    cmd = message.text.split()[0].replace("/", "")
    msg = await message.answer(f"🔄 Fetching {cmd} market data...")
    
    url_map = {"auctions": "usernames?sort=ending", "domains": "domains?sort=ending", 
               "numbers": "numbers?sort=ending", "trending": "?sort=bids", "floor": "?sort=price"}
               
    items = await fetch_market(url_map.get(cmd, ""))
    if not items: 
        return await msg.edit_text("❌ No data found on Fragment.")
    
    # Data ko table ke liye prepare karna
    headers = ["#", "Name", "Price"]
    table_data = []
    for idx, item in enumerate(items[:10], 1): # Top 10 nikalenge
        # Price se "TON" hata kar clean karenge taaki space bache
        clean_price = item['price'].replace("TON", "").strip()
        table_data.append([idx, item['name'], f"{clean_price} TON"])

    title = f"Top {cmd.capitalize()} Auctions"
    
    # Image Generate karna
    img_buffer = create_table_image(title, headers, table_data)
    photo = BufferedInputFile(img_buffer.getvalue(), filename=f"{cmd}_market.png")
    
    # Inline Keyboard Button
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"View {cmd.capitalize()} ↗", url=f"https://fragment.com/{url_map.get(cmd, '').split('?')[0]}")]
    ])
    
    # Purana message delete karke sidha photo bhejna
    await msg.delete()
    await message.answer_photo(
        photo=photo, 
        caption=f"🔥 **{title}**\n\n*Live data scraped from Fragment.*", 
        reply_markup=kb, 
        parse_mode="Markdown"
    )

# ... (Niche ke functions cmd_premium aur cmd_stars waise hi rahenge) ...