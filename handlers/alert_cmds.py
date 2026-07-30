from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db import AsyncSessionLocal
from database.models import TrackedWallet, Reminder
from datetime import datetime

router = Router()

@router.message(Command("track"))
async def cmd_track(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/track <address>`", parse_mode="Markdown")
    async with AsyncSessionLocal() as session:
        session.add(TrackedWallet(user_id=message.from_user.id, address=args[1]))
        await session.commit()
    await message.answer("✅ Wallet added to tracking.")

@router.message(Command("tracking"))
async def cmd_tracking(message: Message):
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(TrackedWallet).where(TrackedWallet.user_id == message.from_user.id))
        wallets = res.scalars().all()
    if not wallets: return await message.answer("No tracked wallets.")
    await message.answer("👁 **Tracked Wallets:**\n" + "\n".join([f"• `{w.address[:10]}...`" for w in wallets]), parse_mode="Markdown")

@router.message(Command("remind"))
async def cmd_remind(message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.answer("Usage: `/remind <username>`", parse_mode="Markdown")
    async with AsyncSessionLocal() as session:
        session.add(Reminder(user_id=message.from_user.id, item_name=args[1]))
        await session.commit()
    await message.answer(f"⏰ Reminder set for {args[1]}.")

@router.message(Command("reminders"))
async def cmd_reminders(message: Message):
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Reminder).where(Reminder.user_id == message.from_user.id))
        rems = res.scalars().all()
    if not rems: return await message.answer("No active reminders.")
    await message.answer("⏰ **Your Reminders:**\n" + "\n".join([f"• {r.item_name}" for r in rems]))