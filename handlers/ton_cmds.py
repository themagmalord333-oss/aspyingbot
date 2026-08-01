from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from ton.api import fetch_ton_balance, fetch_wallet_nfts, fetch_wallet_stats, resolve_contact
from utils.image_gen import create_balance_image

router = Router()

@router.message(Command("balance"))
async def cmd_balance(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/balance <username or address>`", parse_mode="Markdown")

    target = args[1].lower()
    msg = await message.answer(f"🔄 Scanning blockchain for `{target}`...")
    
    data = await fetch_ton_balance(target)

    if "error" in data: 
        return await msg.edit_text(f"❌ Error: {data['error']}")

    # Generating the exact balance image
    img_buffer = create_balance_image(target, data['balance'], data['usd'])
    photo = BufferedInputFile(img_buffer.getvalue(), filename=f"{target}_balance.png")

    # Adding buttons as requested
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Tonviewer ↗", url=f"https://tonviewer.com/{data['address']}"),
            InlineKeyboardButton(text="Track wallet ↗", callback_data=f"track_{data['address'][:10]}")
        ]
    ])

    await msg.delete()
    await message.answer_photo(photo=photo, reply_markup=kb)

@router.message(Command("nft", "portfolio"))
async def cmd_nft(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/nft <address>`", parse_mode="Markdown")

    msg = await message.answer("🔍 Scanning wallet for Fragment NFTs...")
    data = await fetch_wallet_nfts(args[1])

    if "error" in data: 
        return await msg.edit_text("❌ Failed to load portfolio. Check API constraints.")

    if data["total"] == 0: 
        return await msg.edit_text("This wallet holds 0 Fragment Usernames.\n\n🛡 *Powered by Anysnap*", parse_mode="Markdown")

    text = f"🖼 **Wallet Portfolio ({data['total']} Usernames):**\n\n"
    for name in data["items"][:15]: 
        text += f"• @{name.replace('.t.me', '')}\n"

    if data["total"] > 15:
        text += f"\n...and {data['total'] - 15} more."

    text += "\n\n🛡 *Powered by Anysnap*"
    await msg.edit_text(text, parse_mode="Markdown")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/stats <address>`", parse_mode="Markdown")

    msg = await message.answer("🔄 Fetching wallet stats...")
    stats = await fetch_wallet_stats(args[1])

    if "error" in stats: 
        return await msg.edit_text("❌ Error fetching stats.")

    text = (
        f"📊 **Wallet Stats:**\n"
        f"Transactions checked: {stats['total_transactions']}\n"
        f"Active transfers: {stats['recent_activity']}\n\n"
        f"🛡 *Powered by Anysnap*"
    )
    await msg.edit_text(text, parse_mode="Markdown")

@router.message(Command("contact"))
async def cmd_contact(message: Message):
    args = message.text.split()
    if len(args) < 2: 
        return await message.answer("Usage: `/contact <address>`", parse_mode="Markdown")

    msg = await message.answer("🔍 Resolving contact info...")
    info = await resolve_contact(args[1])

    text = f"👤 **Contact Info:**\n{info}\n\n🛡 *Powered by Anysnap*"
    await msg.edit_text(text, parse_mode="Markdown")