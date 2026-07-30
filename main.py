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
        "💠 **Fragment Analytics Bot v2**\n\n"
        "**🔍 Fragment Commands:**\n"
        "/f `<username>` - Get details\n"
        "/auctions - View active auctions\n"
        "/premium - Check TG Premium price\n\n"
        "**💼 Wallet Commands:**\n"
        "/balance `<address>` - Check TON balance\n"
        "/portfolio `<address>` - View NFTs/Usernames\n\n"
        "**🔔 Alerts:**\n"
        "/subscribe `<username>` - Track status\n"
        "/subscriptions - View your list"
    )
    await message.answer(text)

async def background_tasks():
    """APScheduler for background alerts (like price drops) can be added here"""
    print("Scheduler running...")

async def main():
    print("🚀 Initializing Database...")
    await init_db()
    
    print("⏳ Starting Background Scheduler...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(background_tasks, 'interval', minutes=30)
    scheduler.start()

    print("🤖 Bot is starting (Long Polling)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped gracefully.")