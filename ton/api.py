import aiohttp
import os

def get_headers():
    key = os.getenv("TON_API_KEY")
    return {"Authorization": f"Bearer {key}"} if key else {}

async def fetch_ton_balance(address: str) -> dict:
    url = f"https://tonapi.io/v2/accounts/{address}"
    async with aiohttp.ClientSession(headers=get_headers()) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"error": "Account not found or invalid address."}
            data = await response.json()
            return {
                "address": address,
                "balance": data.get("balance", 0) / 1e9,
                "status": data.get("status")
            }

async def fetch_wallet_nfts(address: str) -> dict:
    # Fragment Username Collection Address
    collection = "EQCA14o1-VWhS2efVKHNmEIeM1M6GfM0Dpn-gBWnDBZ_G9Lp"
    url = f"https://tonapi.io/v2/accounts/{address}/nfts?collection={collection}"
    
    async with aiohttp.ClientSession(headers=get_headers()) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"error": "Failed to fetch NFTs"}
            data = await response.json()
            nfts = data.get("nft_items", [])
            names = [nft.get("metadata", {}).get("name", "Unknown") for nft in nfts]
            return {"total": len(names), "items": names}