from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from ton.api import fetch_wallet_stats, resolve_contact

router = Router()

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

@router.message(Command("whales"))
async def cmd_whales(message: Message):
    await message.answer("🐋 **Top Whales (Fragment Collection):**\n\n1. `EQCA14o1-VWhS2efVKHN...`\n2. `EQBvW8Z5huPt351jIG7F...`\n*(Live blockchain indexing required for full global list)*", parse_mode="Markdown")