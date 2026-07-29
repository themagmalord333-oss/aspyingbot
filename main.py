import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

# --- 1. SETUP & CONFIG ---
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TON_API_KEY = os.getenv("TON_API_KEY")

if not BOT_TOKEN or not TON_API_KEY:
    raise ValueError("Missing BOT_TOKEN or TON_API_KEY in .env file!")

# Initialize Bot & Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# --- 2. UTILS: Load Cookies ---
def load_cookies(filepath=".cookies.txt"):
    """Reads simple key=value cookies from file for Fragment auth."""
    cookies = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    cookies[key] = val
    return cookies

# --- 3. SERVICES (Core Functions) ---

async def fetch_fragment_username(username: str) -> dict:
    """Fetches username data directly from Fragment HTML."""
    url = f"https://fragment.com/username/{username}"
    cookies = load_cookies()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"error": f"Failed to fetch. Status code: {response.status}"}
            
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            
            # Basic parsing logic (this might need updates based on Fragment's current DOM)
            status_elem = soup.find("span", class_="tm-section-header-status")
            status = status_elem.text.strip() if status_elem else "Status Unknown"
            
            price_elem = soup.find("div", class_="table-cell-value tm-value icon-before icon-ton")
            price = price_elem.text.strip() if price_elem else "Price not found"
            
            return {
                "username": username,
                "status": status,
                "price": price,
                "url": url
            }

async def fetch_ton_balance(address: str) -> dict:
    """Fetches wallet balance using TonAPI."""
    url = f"https://tonapi.io/v2/accounts/{address}"
    headers = {"Authorization": f"Bearer {TON_API_KEY}"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"error": "Account not found or invalid address."}
            
            data = await response.json()
            balance_ton = data.get("balance", 0) / 1e9  # NanoTON to TON
            return {
                "address": address,
                "balance": balance_ton,
                "status": data.get("status")
            }

# --- 4. TELEGRAM HANDLERS ---

@dp.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "🤖 **Prototype Bot is Live!**\n\n"
        "Available commands for testing:\n"
        "/fragment `<username>` - Test Fragment scraping\n"
        "/balance `<ton_address>` - Test TON API connection"
    )
    await message.answer(text)

@dp.message(Command("fragment"))
async def cmd_fragment(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Usage: `/fragment <username>`")
    
    target = args[1].replace("@", "")
    await message.answer(f"🔍 Checking `@{target}` on Fragment...")
    
    data = await fetch_fragment_username(target)
    
    if "error" in data:
        return await message.answer(f"❌ Error: {data['error']}")
        
    response_text = (
        f"💎 **Fragment Data for @{data['username']}**\n\n"
        f"**Status:** {data['status']}\n"
        f"**Price:** {data['price']} TON\n\n"
        f"[View on Fragment]({data['url']})"
    )
    await message.answer(response_text, disable_web_page_preview=True)

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Usage: `/balance <ton_address>`")
    
    address = args[1]
    await message.answer("🔄 Fetching wallet data from TonAPI...")
    
    data = await fetch_ton_balance(address)
    
    if "error" in data:
        return await message.answer(f"❌ Error: {data['error']}")
        
    response_text = (
        f"💼 **TON Wallet Info**\n\n"
        f"**Address:** `{data['address']}`\n"
        f"**Status:** {data['status']}\n"
        f"**Balance:** `{data['balance']:.2f}` TON"
    )
    await message.answer(response_text)

# --- 5. MAIN ENTRY POINT ---
async def main():
    print("🚀 Starting bot in prototype mode (Long Polling)...")
    # This drops all offline messages so your bot doesn't spam you on startup
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped gracefully.")