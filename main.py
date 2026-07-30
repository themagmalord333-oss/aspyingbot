import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Database and Routers
from database.db import init_db
from handlers.fragment_cmds import router as fragment_router
from handlers.ton_cmds import router as ton_router
from handlers.alert_cmds import router as alert_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN in .env file!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# Include all modular routers
dp.include_router(fragment_router)
dp.include_router(ton_router)
dp.include_router(alert_router)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "💠 **Fragment Analytics Bot MAX**\n\n"
        "🕵️ **Fragment & Usernames**\n"
        "`/f <name>` - Check username\n"
        "`/similar <name>` - Find similar\n"
        "`/history <name>` - Ownership history\n"
        "`/nft <address>` - Wallet NFTs\n"
        "`/contact <address>` - Find owner TG\n\n"
        "🏷 **Auctions & Market**\n"
        "`/auctions` | `/domains` | `/numbers`\n"
        "`/trending` | `/floor` | `/floorhistory`\n\n"
        "👛 **Wallet & Finance**\n"
        "`/balance <add>` | `/stats <add>` | `/whales`\n\n"
        "🔔 **Alerts & Tracking**\n"
        "`/subscribe <name>` | `/subscriptions`\n"
        "`/track <add>` | `/tracking`\n"
        "`/remind <name>` | `/reminders`\n\n"
        "⭐ **Pricing**\n"
        "`/premium` | `/stars`"
    )
    await message.answer(text, parse_mode="Markdown")
