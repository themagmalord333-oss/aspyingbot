import aiohttp
import os

def get_headers():
    # TON_API_KEY .env file me hona zaroori hai better speed ke liye
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

async def fetch_ton_balance(query: str) -> dict:
    account_id = query
    is_username = False
    
    # 1. Determine if the input is a short username or a raw 48-char address
    if not query.endswith(".ton") and not query.endswith(".t.me") and len(query) < 48:
        account_id = f"{query}.t.me"
        is_username = True
    elif query.endswith(".t.me") or query.endswith(".ton"):
        is_username = True
        
    target_address = account_id
    
    # 2. MAGIC FIX: If it's a username, find the wallet that owns this NFT
    if is_username:
        nft_data = await fetch_ton_api(f"nfts/{account_id}")
        if nft_data and "owner" in nft_data and "address" in nft_data["owner"]:
            target_address = nft_data["owner"]["address"]

    # 3. Now fetch the balance of the resolved true wallet address
    data = await fetch_ton_api(f"accounts/{target_address}")
    
    if not data: 
        return {"error": "Account not found on TON Blockchain. (API Key limit ya invalid name)"}
        
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