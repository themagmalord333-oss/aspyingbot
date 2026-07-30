from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from ton.api import fetch_ton_balance, fetch_wallet_nfts

router = Router()

@router.message(Command("balance"))
async def cmd_balance(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Usage: `/balance <ton_address>`", parse_mode="Markdown")
    
    msg = await message.answer("🔄 Fetching wallet data...")
    data = await fetch_ton_balance(args[1])
    
    if "error" in data:
        return await msg.edit_text(f"❌ Error: {data['error']}")
        
    text = (
        f"💼 **TON Wallet Info**\n\n"
        f"**Address:** `{data['address']}`\n"
        f"**Status:** {data['status']}\n"
        f"**Balance:** `{data['balance']:.2f}` TON"
    )
    await msg.edit_text(text, parse_mode="Markdown")

@router.message(Command("portfolio", "nft"))
async def cmd_portfolio(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Usage: `/portfolio <ton_address>`", parse_mode="Markdown")
        
    msg = await message.answer("🔍 Scanning wallet for Fragment Usernames...")
    data = await fetch_wallet_nfts(args[1])
    
    if "error" in data:
        return await msg.edit_text("❌ Failed to load portfolio.")
        
    if data["total"] == 0:
        return await msg.edit_text("This wallet holds 0 Fragment Usernames.")
        
    text = f"🖼 **Wallet Portfolio ({data['total']} Usernames):**\n\n"
    for name in data["items"][:15]: # Show max 15 to avoid text limit
        text += f"• @{name.replace('.t.me', '')}\n"
        
    await msg.edit_text(text)