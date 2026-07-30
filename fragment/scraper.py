import aiohttp
from bs4 import BeautifulSoup
from utils.cookies import load_cookies

BASE_URL = "https://fragment.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

async def fetch_fragment_username(username: str) -> dict:
    url = f"{BASE_URL}/username/{username}"
    async with aiohttp.ClientSession(cookies=load_cookies(), headers=HEADERS) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"error": f"Failed to fetch. Status code: {response.status}"}
            
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            
            status_elem = soup.find("span", class_="tm-section-header-status")
            status = status_elem.text.strip() if status_elem else "Status Unknown"
            
            price_elem = soup.find("div", class_="table-cell-value tm-value icon-before icon-ton")
            price = price_elem.text.strip() if price_elem else "N/A"
            
            owner_elem = soup.find("a", class_="tm-wallet")
            owner = owner_elem.text.strip() if owner_elem else "Fragment"

            return {"username": username, "status": status, "price": price, "owner": owner, "url": url}

async def fetch_active_auctions(item_type="usernames"):
    """Fetches real ending soon auctions from fragment."""
    url = f"{BASE_URL}/{item_type}?sort=ending"
    async with aiohttp.ClientSession(cookies=load_cookies(), headers=HEADERS) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return []
            
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.find_all("tr", class_="tm-row-selectable")
            
            auctions = []
            for row in rows[:10]: # Top 10
                title_elem = row.find("div", class_="table-cell-value tm-value")
                price_elem = row.find("div", class_="table-cell-value tm-value icon-before icon-ton")
                if title_elem and price_elem:
                    auctions.append({
                        "name": title_elem.text.strip(),
                        "price": price_elem.text.strip()
                    })
            return auctions

async def fetch_premium_price():
    """Scrape real TG Premium price in TON from Fragment"""
    url = f"{BASE_URL}/premium"
    async with aiohttp.ClientSession(cookies=load_cookies(), headers=HEADERS) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "Unknown"
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            price_elem = soup.find("div", class_="tm-min-btn-value icon-before icon-ton")
            return price_elem.text.strip() if price_elem else "Unknown"