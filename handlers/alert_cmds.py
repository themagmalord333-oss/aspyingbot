from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db import AsyncSessionLocal
from database.models import Subscription

router = Router()

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Usage: `/subscribe <username>`", parse_mode="Markdown")
        
    target = args[1].replace("@", "")
    
    async with AsyncSessionLocal() as session:
        sub = Subscription(user_id=message.from_user.id, username=target)
        session.add(sub)
        await session.commit()
        
    await message.answer(f"✅ Subscribed! You will receive alerts for @{target}.")

@router.message(Command("subscriptions"))
async def cmd_subs(message: Message):
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Subscription).where(Subscription.user_id == message.from_user.id))
        subs = result.scalars().all()
        
    if not subs:
        return await message.answer("You have no active subscriptions.")
        
    text = "🔔 **Your Subscriptions:**\n"
    for s in subs:
        text += f"• @{s.username}\n"
    await message.answer(text)