import aiohttp
import os
from bs4 import BeautifulSoup

def get_headers():
    key = os.getenv("TON_API_KEY")
    return {"Authorization": f"Bearer {key}"} if key else {}

async def fetch_ton_api(endpoint: str):
    url = f"https://tonapi.io/v2/{endpoint}"
    try:
        async with aiohttp.ClientSession(headers=get_headers()) as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception:
        pass
    return None

async def fetch_ton_price():
    """Fetches live TON to USD price."""
    url = "https://tonapi.io/v2/rates?tokens=ton&currencies=usd"
    try:
        async with aiohttp.ClientSession(headers=get_headers()) as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("rates", {}).get("TON", {}).get("prices", {}).get("USD", 0)
    except:
        pass
    return 0

async def resolve_fragment_owner(username: str):
    """Scrapes Fragment to find the actual owner wallet/domain of a username."""
    url = f"https://fragment.com/username/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    # Targeting the owner's wallet link on Fragment
                    wallet_link = soup.find("a", class_="tm-wallet")
                    if wallet_link:
                        href = wallet_link.get("href", "")
                        if "tonviewer.com/" in href:
                            return href.split("tonviewer.com/")[1].strip()
                        return wallet_link.get_text(strip=True)
    except Exception:
        pass
    return None

async def fetch_ton_balance(query: str) -> dict:
    # 48 characters raw wallet address ko bypass karwayenge
    target_address = query
    
    if len(query) < 48 and not query.endswith(".ton"):
        query = query.lower().replace("@", "")
        # Fragment se owner ka asli address nikalenge
        owner = await resolve_fragment_owner(query)
        if owner:
            target_address = owner
        else:
            target_address = f"{query}.t.me"

    # Ab resolved owner address ka data fetch karenge
    data = await fetch_ton_api(f"accounts/{target_address}")
    
    if not data: 
        return {"error": "Account not found on TON Blockchain."}
        
    balance_ton = data.get("balance", 0) / 1e9
    address = data.get("address", target_address) 
    
    usd_price = await fetch_ton_price()
    balance_usd = balance_ton * usd_price
    
    return {
        "address": address, 
        "balance": balance_ton, 
        "usd": balance_usd,
        "status": data.get("status", "Unknown")
    }

async def fetch_wallet_nfts(address: str) -> dict:
    collection = "EQCA14o1-VWhS2efVKHNmEIeM1M6GfM0Dpn-gBWnDBZ_G9Lp"
    data = await fetch_ton_api(f"accounts/{address}/nfts?collection={collection}")
    if not data: return {"error": "Failed to fetch NFTs."}
    nfts = data.get("nft_items", [])
    names = [nft.get("metadata", {}).get("name", "Unknown") for nft in nfts]
    return {"total": len(names), "items": names}

async def fetch_wallet_stats(address: str) -> dict:
    data = await fetch_ton_api(f"accounts/{address}/events?limit=50")
    if not data: return {"error": "Could not fetch stats."}
    events = data.get("events", [])
    sent = sum(1 for e in events if e.get("in_progress") == False)
    return {"total_transactions": len(events), "recent_activity": sent}

async def resolve_contact(address: str):
    data = await fetch_ton_api(f"accounts/{address}/dns/backresolve")
    if data and data.get("domain"):
        return f"Domain Name: {data['domain']}"
    return "No public Telegram/DNS linked to this wallet."
