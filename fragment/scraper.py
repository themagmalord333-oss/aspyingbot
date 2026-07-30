import aiohttp
from bs4 import BeautifulSoup
from utils.cookies import load_cookies

BASE_URL = "[https://fragment.com](https://fragment.com)"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

async def fetch_soup(url: str):
    async with aiohttp.ClientSession(cookies=load_cookies(), headers=HEADERS) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return BeautifulSoup(await resp.text(), "html.parser")
    return None

async def fetch_fragment_username(username: str) -> dict:
    soup = await fetch_soup(f"{BASE_URL}/username/{username}")
    if not soup: return {"error": "Failed to fetch data."}
    
    status = soup.find("span", class_="tm-section-header-status")
    price = soup.find("div", class_="table-cell-value tm-value icon-before icon-ton")
    owner = soup.find("a", class_="tm-wallet")
    
    return {
        "status": status.text.strip() if status else "Unknown",
        "price": price.text.strip() if price else "N/A",
        "owner": owner.text.strip() if owner else "Fragment"
    }

async def fetch_similar(query: str) -> list:
    soup = await fetch_soup(f"{BASE_URL}/?query={query}")
    if not soup: return []
    items = soup.find_all("tr", class_="tm-row-selectable")
    return [i.find("div", class_="table-cell-value").text.strip() for i in items[:5] if i.find("div", class_="table-cell-value")]

async def fetch_history(username: str) -> list:
    soup = await fetch_soup(f"{BASE_URL}/username/{username}")
    if not soup: return []
    history = []
    rows = soup.find_all("tr")
    for row in rows:
        date = row.find("div", class_="tm-datetime")
        price = row.find("div", class_="table-cell-value tm-value icon-before icon-ton")
        if date and price:
            history.append(f"{date.text.strip()} - {price.text.strip()}")
    return history[:5]

async def fetch_market(type_url: str) -> list:
    soup = await fetch_soup(f"{BASE_URL}/{type_url}")
    if not soup: return []
    items = []
    for row in soup.find_all("tr", class_="tm-row-selectable")[:10]:
        title = row.find("div", class_="table-cell-value tm-value")
        price = row.find("div", class_="table-cell-value tm-value icon-before icon-ton")
        if title and price:
            items.append({"name": title.text.strip(), "price": price.text.strip()})
    return items

async def fetch_premium_packages():
    """Scrapes Telegram Premium packages directly from Fragment."""
    soup = await fetch_soup(f"{BASE_URL}/premium")
    if not soup: return []
    packages = []
    options = soup.find_all("label", class_="tm-form-radio")
    for opt in options:
        title_elem = opt.find("div", class_="tm-form-radio-title")
        price_elem = opt.find("div", class_="tm-form-radio-value")
        if title_elem and price_elem:
            packages.append({"title": title_elem.text.strip(), "price": price_elem.text.strip()})
    return packages

async def fetch_stars_packages():
    """Scrapes Telegram Stars packages directly from Fragment."""
    soup = await fetch_soup(f"{BASE_URL}/stars")
    if not soup: return []
    packages = []
    options = soup.find_all("label", class_="tm-form-radio")
    for opt in options:
        title_elem = opt.find("div", class_="tm-form-radio-title")
        price_elem = opt.find("div", class_="tm-form-radio-value")
        if title_elem and price_elem:
            packages.append({"title": title_elem.text.strip(), "price": price_elem.text.strip()})
    return packages