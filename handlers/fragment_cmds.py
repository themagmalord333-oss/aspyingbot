from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from fragment.scraper import fetch_fragment_username, fetch_active_auctions, fetch_premium_price

router = Router()

@router.message(Command("fragment", "f"))
async def cmd_fragment(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Usage: `/fragment <username>`", parse_mode="Markdown")
    
    target = args[1].replace("@", "")
    msg = await message.answer(f"🔍 Checking `@{target}` on Fragment...", parse_mode="Markdown")
    
    data = await fetch_fragment_username(target)
    if "error" in data:
        return await msg.edit_text(f"❌ Error: {data['error']}")
        
    text = (
        f"💎 **Fragment Data for @{data['username']}**\n\n"
        f"**Status:** {data['status']}\n"
        f"**Price:** {data['price']} TON\n"
        f"**Owner:** `{data['owner']}`\n\n"
        f"[View on Fragment]({data['url']})"
    )
    await msg.edit_text(text, parse_mode="Markdown", disable_web_page_preview=True)

@router.message(Command("auctions"))
async def cmd_auctions(message: Message):
    msg = await message.answer("🔄 Fetching active username auctions...")
    auctions = await fetch_active_auctions("usernames")
    
    if not auctions:
        return await msg.edit_text("❌ No active auctions found or blocked by Fragment.")
        
    text = "🔥 **Top Ending Soon Auctions:**\n\n"
    for item in auctions:
        text += f"• `{item['name']}` : **{item['price']} TON**\n"
        
    await msg.edit_text(text, parse_mode="Markdown")

@router.message(Command("premium"))
async def cmd_premium(message: Message):
    price = await fetch_premium_price()
    await message.answer(f"⭐️ **Telegram Premium via Fragment:**\n\nCurrent Price: **{price} TON**", parse_mode="Markdown")