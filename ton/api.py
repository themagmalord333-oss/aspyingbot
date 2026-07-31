import aiohttp
import os

def get_headers():
    key = os.getenv("TON_API_KEY")
    return {"Authorization": f"Bearer {key}"} if key else {}

async def fetch_ton_api(endpoint: str):
    url = f"https://tonapi.io/v2/{endpoint}"
    try:
        async with aiohttp.ClientSession(headers=get_headers()) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        pass
    return None

async def fetch_ton_balance(address: str) -> dict:
    data = await fetch_ton_api(f"accounts/{address}")
    if not data: return {"error": "Account not found."}
    return {"address": address, "balance": data.get("balance", 0) / 1e9, "status": data.get("status", "Unknown")}

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