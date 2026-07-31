from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from ton.api import fetch_ton_balance, fetch_wallet_nfts, fetch_wallet_stats, resolve_contact

router = Router()

@router.message(Command("balance"))
async def cmd_balance(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/balance <address>`", parse_mode="Markdown")
    
    msg = await message.answer("🔄 Fetching wallet data...")
    data = await fetch_ton_balance(args[1])
    
    if "error" in data: return await msg.edit_text(f"❌ Error: {data['error']}")
        
    text = (
        f"💼 **TON Wallet Info**\n\n"
        f"**Address:** `{data['address']}`\n"
        f"**Status:** {data['status']}\n"
        f"**Balance:** `{data['balance']:.2f}` TON"
    )
    await msg.edit_text(text, parse_mode="Markdown")

@router.message(Command("nft", "portfolio"))
async def cmd_nft(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/nft <address>`", parse_mode="Markdown")
        
    msg = await message.answer("🔍 Scanning wallet for Fragment NFTs...")
    data = await fetch_wallet_nfts(args[1])
    
    if "error" in data: return await msg.edit_text("❌ Failed to load portfolio. Check TON_API_KEY.")
    if data["total"] == 0: return await msg.edit_text("This wallet holds 0 Fragment Usernames.")
        
    text = f"🖼 **Wallet Portfolio ({data['total']} Usernames):**\n\n"
    for name in data["items"][:15]: 
        text += f"• @{name.replace('.t.me', '')}\n"
        
    await msg.edit_text(text)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/stats <address>`", parse_mode="Markdown")
    stats = await fetch_wallet_stats(args[1])
    if "error" in stats: return await message.answer("❌ Error fetching stats.")
    await message.answer(f"📊 **Wallet Stats:**\nTransactions checked: {stats['total_transactions']}\nActive transfers: {stats['recent_activity']}", parse_mode="Markdown")

@router.message(Command("contact"))
async def cmd_contact(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/contact <address>`", parse_mode="Markdown")
    info = await resolve_contact(args[1])
    await message.answer(f"👤 **Contact Info:**\n{info}", parse_mode="Markdown")