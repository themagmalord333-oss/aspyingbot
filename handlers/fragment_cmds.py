from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from fragment.scraper import *

router = Router()

@router.message(Command("fragment", "f"))
async def cmd_fragment(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/f <username>`", parse_mode="Markdown")
    target = args[1].replace("@", "")
    msg = await message.answer(f"🔍 Checking `@{target}`...")
    
    data = await fetch_fragment_username(target)
    if "error" in data: return await msg.edit_text("❌ Error fetching data.")
    
    text = (f"💎 **Fragment Data for @{target}**\n\n"
            f"**Status:** {data['status']}\n**Price:** {data['price']} TON\n**Owner:** `{data['owner']}`")
    await msg.edit_text(text, parse_mode="Markdown")

@router.message(Command("similar"))
async def cmd_similar(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/similar <name>`", parse_mode="Markdown")
    items = await fetch_similar(args[1])
    await message.answer("🔍 **Similar Names:**\n" + "\n".join(items) if items else "No similar names found.", parse_mode="Markdown")

@router.message(Command("history", "floorhistory"))
async def cmd_history(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/history <username>`", parse_mode="Markdown")
    hist = await fetch_history(args[1].replace("@", ""))
    await message.answer("📜 **History:**\n\n" + "\n".join(hist) if hist else "No history found.", parse_mode="Markdown")

@router.message(Command("auctions", "domains", "numbers", "trending", "floor"))
async def cmd_markets(message: Message):
    cmd = message.text.split()[0].replace("/", "")
    msg = await message.answer(f"🔄 Fetching {cmd} market...")
    
    url_map = {"auctions": "usernames?sort=ending", "domains": "domains?sort=ending", 
               "numbers": "numbers?sort=ending", "trending": "?sort=bids", "floor": "?sort=price"}
               
    items = await fetch_market(url_map.get(cmd, ""))
    if not items: return await msg.edit_text("❌ No data found.")
    
    text = f"🔥 **Top {cmd.capitalize()}:**\n\n"
    for i in items: text += f"• `{i['name']}` : **{i['price']} TON**\n"
    await msg.edit_text(text, parse_mode="Markdown")

@router.message(Command("premium", "stars"))
async def cmd_pricing(message: Message):
    cmd = message.text.split()[0].replace("/", "")
    price = await fetch_pricing(cmd)
    await message.answer(f"⭐️ **Telegram {cmd.capitalize()} Price:**\n**{price} TON**", parse_mode="Markdown")