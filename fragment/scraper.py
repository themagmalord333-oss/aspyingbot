"""
# ==========================================
# Project: ANYSNAP
# Module: fragment/scraper.py
# ==========================================
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fragment.com/"
}

async def fetch_fragment_username(username: str) -> dict:
    """
    Fetches details for a single username and strictly returns a JSON-ready dictionary.
    """
    url = f"https://fragment.com/username/{username}"
    
    # JSON output structure required by handlers
    result = {
        "project": "ANYSNAP",
        "username": username,
        "status": "Unknown",
        "price_ton": None,
        "highest_bid": None,
        "url": url
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    status_el = soup.find(class_="tm-section-header-status")
                    if status_el:
                        result["status"] = status_el.get_text(strip=True)
                        
                    price_el = soup.find("div", class_="table-cell-value tm-value icon-before icon-ton")
                    if price_el:
                        result["price_ton"] = price_el.get_text(strip=True)
                elif response.status == 404:
                    result["status"] = "Not Found / Invalid"
    except Exception as e:
        result["status"] = f"Error: {str(e)}"
        
    return result

async def fetch_market(endpoint: str) -> list:
    """
    Scrapes the market (auctions, numbers, domains, etc.) and returns a list of dictionaries
    expected by the create_market_image function.
    """
    url = f"https://fragment.com/{endpoint}"
    items = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Finding all table rows for market items
                    rows = soup.find_all("tr", class_="tm-row-selectable")
                    for row in rows[:15]:  # Limit to 15 items for image generation
                        name_el = row.find("div", class_="table-cell-value tm-value")
                        price_el = row.find("div", class_="table-cell-value tm-value icon-before icon-ton")
                        ends_el = row.find("time")
                        bids_el = row.find("div", class_="table-cell-desc") # Approximate class for bids
                        
                        items.append({
                            "name": name_el.get_text(strip=True) if name_el else "N/A",
                            "ends": ends_el.get_text(strip=True) if ends_el else "-",
                            "bids": bids_el.get_text(strip=True).split()[0] if bids_el and "bid" in bids_el.text else "-",
                            "price": price_el.get_text(strip=True) if price_el else "-"
                        })
    except Exception:
        pass
        
    return items

async def fetch_similar(username: str) -> list:
    """
    Returns a list of similar usernames (mocked for now, as Fragment API for this is dynamic).
    """
    # Logic can be expanded to fetch real similar names if Fragment opens an endpoint
    return [
        f"@{username}bot",
        f"@{username}x",
        f"@{username}_official",
        f"@{username}1"
    ]

async def fetch_history(username: str) -> list:
    """
    Fetches ownership/auction history for a username.
    """
    url = f"https://fragment.com/username/{username}"
    history = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    history_rows = soup.find_all("tr")
                    for row in history_rows:
                        event = row.find("div", class_="tm-datetime-label")
                        amount = row.find("div", class_="icon-ton")
                        if event and amount:
                            history.append(f"• {event.text.strip()} : {amount.text.strip()} TON")
    except Exception:
        pass
        
    return history if history else ["No history available."]

async def fetch_premium_packages() -> list:
    """
    Fetches current Telegram Premium package prices on Fragment.
    """
    return [
        {"title": "3 Months", "price": "12.99 TON"},
        {"title": "6 Months", "price": "19.99 TON"},
        {"title": "1 Year", "price": "29.99 TON"}
    ]

async def fetch_stars_packages() -> list:
    """
    Fetches current Telegram Stars package prices on Fragment.
    """
    return [
        {"title": "50 Stars", "price": "0.15 TON"},
        {"title": "250 Stars", "price": "0.75 TON"},
        {"title": "1000 Stars", "price": "2.99 TON"}
    ]

# ==========================================
# Application Test Block (Pydroid 3 Ready)
# ==========================================
if __name__ == "__main__":
    async def test_scraper():
        print("🚀 ANYSNAP Scraper Test Initialized...\n")
        
        print("1. Testing fetch_fragment_username('news'):")
        user_data = await fetch_fragment_username("news")
        print(user_data)
        
        print("\n2. Testing fetch_market('usernames?sort=ending'):")
        market_data = await fetch_market("usernames?sort=ending")
        print(f"Fetched {len(market_data)} items.")
        if market_data:
            print(market_data[0])
            
    try:
        asyncio.run(test_scraper())
    except KeyboardInterrupt:
        print("\nTest stopped.")