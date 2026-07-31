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
                else:
                    print(f"Fragment blocked the request. Status Code: {resp.status}")
    except Exception as e:
        print(f"Network Error: {e}")
    return None

async def fetch_fragment_username(username: str) -> dict:
    url = BASE_URL + '/username/' + username
    soup = await fetch_soup(url)
    if not soup: return {"error": "Failed to fetch data."}
    
    # Tag-less fetching (Only relying on classes)
    status = soup.find(class_="tm-section-header-status")
    price = soup.find(class_=lambda c: c and "icon-ton" in c and "tm-value" in c)
    if not price: price = soup.find(class_="tm-value")
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
    rows = soup.find_all("tr")
    for row in rows[:5]:
        val = row.find(class_="table-cell-value")
        if val and val.text.strip().startswith('@'):
            items.append(val.text.strip())
    return items

async def fetch_history(username: str) -> list:
    url = BASE_URL + '/username/' + username
    soup = await fetch_soup(url)
    if not soup: return []
    history = []
    rows = soup.find_all("tr")
    for row in rows:
        date = row.find(class_="tm-datetime")
        price = row.find(class_=lambda c: c and "icon-ton" in c)
        if date and price:
            history.append(f"{date.text.strip()} - {price.text.strip()}")
    return history[:5]

async def fetch_market(type_url: str) -> list:
    url = BASE_URL + '/' + type_url
    soup = await fetch_soup(url)
    if not soup: return []
    items = []
    rows = soup.find_all("tr")
    for row in rows:
        title = row.find(class_="tm-value")
        price = row.find(class_=lambda c: c and "icon-ton" in c)
        if title and price and "TON" in price.text:
            items.append({"name": title.text.strip(), "price": price.text.strip()})
    return items[:10]

async def fetch_premium_packages():
    url = BASE_URL + '/premium'
    soup = await fetch_soup(url)
    if not soup: return []
    packages = []
    titles = soup.find_all(class_="tm-form-radio-title")
    prices = soup.find_all(class_="tm-form-radio-value")
    for t, p in zip(titles, prices):
        packages.append({"title": t.text.strip(), "price": p.text.strip()})
    return packages

async def fetch_stars_packages():
    url = BASE_URL + '/stars'
    soup = await fetch_soup(url)
    if not soup: return []
    packages = []
    titles = soup.find_all(class_="tm-form-radio-title")
    prices = soup.find_all(class_="tm-form-radio-value")
    for t, p in zip(titles, prices):
        packages.append({"title": t.text.strip(), "price": p.text.strip()})
    return packages