import aiohttp
from bs4 import BeautifulSoup
from utils.cookies import load_cookies
import json

BASE_URL = 'https://fragment.com'
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

async def fetch_soup(url: str):
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(cookies=load_cookies(), headers=HEADERS, timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return BeautifulSoup(await resp.text(), "html.parser")
    except Exception as e:
        pass
    return None

async def fetch_fragment_username(username: str) -> dict:
    url = BASE_URL + '/username/' + username
    soup = await fetch_soup(url)
    if not soup: return {"error": "Failed to fetch data."}
    
    status = soup.find(class_="tm-section-header-status")
    price = soup.find(class_=lambda c: c and "tm-value" in c)
    owner = soup.find(class_="tm-wallet")
    
    return {
        "target_username": username,
        "status": status.text.strip() if status else "Unknown",
        "current_price": price.text.strip() if price else "N/A",
        "owner_wallet": owner.text.strip() if owner else "Fragment"
    }

async def fetch_similar(query: str) -> list:
    url = BASE_URL + '/?query=' + query
    soup = await fetch_soup(url)
    if not soup: return []
    items = []
    for row in soup.find_all("tr"):
        val = row.find(class_="table-cell-value")
        if val and val.text.strip().startswith('@'):
            items.append(val.text.strip())
    return items[:5]

async def fetch_history(username: str) -> list:
    url = BASE_URL + '/username/' + username
    soup = await fetch_soup(url)
    if not soup: return []
    history = []
    for row in soup.find_all("tr"):
        texts = [t.text.strip() for t in row.find_all("div") if t.text.strip()]
        if len(texts) >= 2:
            history.append(f"{texts[0]} - {texts[-1]}")
    return history[:5]

async def fetch_market(type_url: str) -> list:
    url = BASE_URL + '/' + type_url
    soup = await fetch_soup(url)
    if not soup: return []
    items = []
    # Ultra-aggressive table parsing
    for row in soup.find_all("tr"):
        vals = [v.text.strip() for v in row.find_all("div", class_=lambda c: c and "value" in c) if v.text.strip()]
        if not vals:
            vals = [td.text.strip() for td in row.find_all("td") if td.text.strip()]
            
        if len(vals) >= 2:
            name = vals[0]
            price = next((v for v in vals if "TON" in v or "GRAM" in v), vals[-1])
            items.append({"name": name, "price": price})
    return items[:10]

async def fetch_premium_packages():
    url = BASE_URL + '/premium'
    soup = await fetch_soup(url)
    if not soup: return []
    packages = []
    for label in soup.find_all("label"):
        texts = [div.text.strip() for div in label.find_all("div") if div.text.strip()]
        if len(texts) >= 2:
            packages.append({"title": texts[0], "price": texts[-1]})
    return packages

async def fetch_stars_packages():
    url = BASE_URL + '/stars'
    soup = await fetch_soup(url)
    if not soup: return []
    packages = []
    for label in soup.find_all("label"):
        texts = [div.text.strip() for div in label.find_all("div") if div.text.strip()]
        if len(texts) >= 2:
            packages.append({"title": texts[0], "price": texts[-1]})
    return packages