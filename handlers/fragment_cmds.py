from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from fragment.scraper import fetch_fragment_username, fetch_market, fetch_similar, fetch_history
from utils.image_gen import create_market_image, create_status_image, create_similar_image, create_history_image

router = Router()

@router.message(Command("fragment", "f"))
async def cmd_fragment(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/f <username>`", parse_mode="Markdown")

    target = args[1].replace("@", "")
    msg = await message.answer(f"🔍 Checking `@{target}`...")

    try:
        data = await fetch_fragment_username(target)
        status_text = data.get("status", "Status unknown.")
        
        # JSON ki jagah ab Status Image jayegi
        img_buffer = create_status_image(target, status_text)
        photo = BufferedInputFile(img_buffer.getvalue(), filename=f"{target}_status.png")

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="View on Fragment ↗", url=f"https://fragment.com/username/{target}")]
        ])
        
        await msg.delete()
        await message.answer_photo(photo=photo, reply_markup=kb)
    except Exception as e:
        await msg.edit_text(f"❌ Application Error: `{str(e)}`", parse_mode="Markdown")


@router.message(Command("auctions", "domains", "numbers", "trending", "floor"))
async def cmd_markets(message: Message):
    cmd = message.text.split()[0].replace("/", "")
    msg = await message.answer(f"🔄 Fetching {cmd} data...")

    try:
        url_map = {"auctions": "usernames?sort=ending", "domains": "domains?sort=ending", 
                   "numbers": "numbers?sort=ending", "trending": "?sort=bids", "floor": "?sort=price"}

        items = await fetch_market(url_map.get(cmd, ""))
        if not items: 
            return await msg.edit_text("❌ No data found on Fragment.")

        title = f"Top {cmd.capitalize()} Auctions"
        if cmd == "trending": title = "Trending Auctions"
        
        col_name = "Domain" if cmd == "domains" else ("Number" if cmd == "numbers" else "Username")

        img_buffer = create_market_image(title, col_name, items)
        photo = BufferedInputFile(img_buffer.getvalue(), filename=f"{cmd}_market.png")

        target_url = url_map.get(cmd, '').split('?')[0]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"View {cmd.capitalize()} ↗", url=f"https://fragment.com/{target_url}")]
        ])

        await msg.delete()
        await message.answer_photo(photo=photo, reply_markup=kb)

    except Exception as e:
        await msg.edit_text(f"❌ Image Generator Error: `{str(e)}`", parse_mode="Markdown")


@router.message(Command("similar"))
async def cmd_similar(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/similar <name>`", parse_mode="Markdown")
        
    target = args[1].replace("@", "")
    msg = await message.answer("🔍 Finding similar names...")
    
    try:
        items = await fetch_similar(target)
        if not items:
            return await msg.edit_text("❌ No similar names found.")
            
        # Text ki jagah Similar Image jayegi
        img_buffer = create_similar_image(target, items)
        photo = BufferedInputFile(img_buffer.getvalue(), filename="similar.png")
        
        await msg.delete()
        await message.answer_photo(photo=photo)
    except Exception as e:
        await msg.edit_text(f"❌ Error: `{str(e)}`", parse_mode="Markdown")


@router.message(Command("history", "floorhistory"))
async def cmd_history(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/history <username>`", parse_mode="Markdown")
        
    target = args[1].replace("@", "")
    msg = await message.answer("📜 Fetching ownership history...")
    
    try:
        hist = await fetch_history(target)
        if not hist or hist[0] == "No history available.":
            return await msg.edit_text("❌ No history found.")
            
        # Text ki jagah History Image jayegi
        img_buffer = create_history_image(target, hist)
        photo = BufferedInputFile(img_buffer.getvalue(), filename="history.png")
        
        await msg.delete()
        await message.answer_photo(photo=photo)
    except Exception as e:
        await msg.edit_text(f"❌ Error: `{str(e)}`", parse_mode="Markdown")