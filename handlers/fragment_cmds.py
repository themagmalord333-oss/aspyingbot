from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from fragment.scraper import *
from utils.image_gen import create_table_image
import json

router = Router()

@router.message(Command("fragment", "f"))
async def cmd_fragment(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/f <username>`", parse_mode="Markdown")
        
    target = args[1].replace("@", "")
    msg = await message.answer(f"🔍 Searching Fragment DB for `@{target}`...")
    
    try:
        data = await fetch_fragment_username(target)
        if "error" in data: 
            return await msg.edit_text("❌ Error fetching data.")
        
        # Strictly returning data formatted as a JSON object
        json_output = json.dumps(data, indent=4)
        text = f"**Search Result:**\n```json\n{json_output}\n```\n🛡 *Powered by ANYSNAP*"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="View on Fragment ↗", url=f"https://fragment.com/username/{target}")]
        ])
        await msg.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        
    except Exception as e:
        await msg.edit_text(f"❌ Application Error: `{str(e)}`", parse_mode="Markdown")

@router.message(Command("auctions", "domains", "numbers", "trending", "floor"))
async def cmd_markets(message: Message):
    cmd = message.text.split()[0].replace("/", "")
    msg = await message.answer(f"🔄 Fetching {cmd} market data...")
    
    try:
        url_map = {"auctions": "usernames?sort=ending", "domains": "domains?sort=ending", 
                   "numbers": "numbers?sort=ending", "trending": "?sort=bids", "floor": "?sort=price"}
                   
        items = await fetch_market(url_map.get(cmd, ""))
        if not items: 
            return await msg.edit_text("❌ No data found on Fragment.")
        
        headers = ["#", "Name", "Price"]
        table_data = []
        for idx, item in enumerate(items[:10], 1):
            clean_price = item['price'].replace("TON", "").strip()
            table_data.append([idx, item['name'], f"{clean_price} TON"])

        title = f"Top {cmd.capitalize()} Auctions"
        
        img_buffer = create_table_image(title, headers, table_data)
        photo = BufferedInputFile(img_buffer.getvalue(), filename=f"{cmd}_market.png")
        
        # Fallback URL parsing avoiding Markdown format issues
        target_url = url_map.get(cmd, '').split('?')[0]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"View {cmd.capitalize()} ↗", url=f"https://fragment.com/{target_url}")]
        ])
        
        await msg.delete()
        await message.answer_photo(
            photo=photo, 
            caption=f"🔥 **{title}**\n\n*Live data scraped from Fragment.*\n🛡 *Powered by ANYSNAP*", 
            reply_markup=kb, 
            parse_mode="Markdown"
        )
    except Exception as e:
        await msg.edit_text(f"❌ Image Generator Error: `{str(e)}`", parse_mode="Markdown")

@router.message(Command("premium"))
async def cmd_premium(message: Message):
    msg = await message.answer("🔄 Fetching Premium prices...")
    try:
        packages = await fetch_premium_packages()
        if not packages: return await msg.edit_text("❌ Failed to fetch Premium data.")
        
        text = ""
        for p in packages:
            text += f"⭐ **{p['title']}**: {p['price']} GRAM\n"
            
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Buy Premium ↗", url="https://fragment.com/premium")]
        ])
        await msg.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Error: `{str(e)}`", parse_mode="Markdown")

@router.message(Command("stars"))
async def cmd_stars(message: Message):
    msg = await message.answer("🔄 Fetching Stars prices...")
    try:
        packages = await fetch_stars_packages()
        if not packages: return await msg.edit_text("❌ Failed to fetch Stars data.")
        
        text = ""
        for p in packages:
            text += f"🌟 **{p['title']}**: {p['price']} GRAM\n"
            
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Buy Stars ↗", url="https://fragment.com/stars")]
        ])
        await msg.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Error: `{str(e)}`", parse_mode="Markdown")