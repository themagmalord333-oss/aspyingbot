import aiohttp
import os

def get_headers():
    key = os.getenv("TON_API_KEY")
    return {"Authorization": f"Bearer {key}"} if key else {}

async def fetch_ton_api(endpoint: str):
    url = f"https://tonapi.io/v2/{endpoint}"
    async with aiohttp.ClientSession(headers=get_headers()) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
    return None

async def fetch_wallet_stats(address: str) -> dict:
    events = await fetch_ton_api(f"accounts/{address}/events?limit=50")
    if not events: return {"error": "Could not fetch stats"}
    
    sent = sum(1 for e in events.get("events", []) if e.get("in_progress") == False)
    return {"total_transactions": len(events.get("events", [])), "recent_activity": sent}

async def resolve_contact(address: str):
    # Try to find a .ton DNS linked to wallet
    dns = await fetch_ton_api(f"accounts/{address}/dns/backresolve")
    if dns and dns.get("domain"):
        return f"Domain Name: {dns['domain']}"
    return "No public Telegram/DNS linked to this wallet."