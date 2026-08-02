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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fragment.com/"
}

async def fetch_fragment_username(username: str) -> dict:
    username = username.lower().replace("@", "").strip()
    url = f"https://fragment.com/username/{username}"
    
    result = {
        "username": username,
        "status": "Unknown",
        "ends_in": "",
        "highest_bid": "0",
        "bid_step": "0",
        "min_bid": "0",
        "usd_highest": "-",
        "usd_min": "-",
        "sold_price": "-",
        "info_text": "This username is not available."
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
                    
                    status_lower = result["status"].lower()
                    
                    if "banned" in status_lower:
                        result["info_text"] = "This username is banned and cannot be registered or purchased."
                    elif "available" in status_lower:
                        result["info_text"] = "This username is available for auction."
                    elif "sold" in status_lower:
                        result["info_text"] = "This username has been sold."
                        
                    time_el = soup.find("time")
                    if time_el:
                        result["ends_in"] = time_el.get_text(strip=True)

                    values = soup.find_all("div", class_="table-cell-value tm-value icon-before icon-ton")
                    usd_values = soup.find_all("div", class_="table-cell-desc")

                    if "auction" in status_lower and len(values) >= 3:
                        result["highest_bid"] = values[0].get_text(strip=True)
                        result["bid_step"] = values[1].get_text(strip=True)
                        result["min_bid"] = values[2].get_text(strip=True)
                        
                        if len(usd_values) >= 3:
                            result["usd_highest"] = usd_values[0].get_text(strip=True).replace("~", "≈ ")
                            result["usd_min"] = usd_values[2].get_text(strip=True).replace("~", "≈ ")
                            
                    elif "sold" in status_lower and len(values) >= 1:
                        result["sold_price"] = values[0].get_text(strip=True)
                    elif "available" in status_lower and len(values) >= 1:
                        result["min_bid"] = values[0].get_text(strip=True)

                elif response.status == 404:
                    result["status"] = "Not Found"
                    result["info_text"] = "Username not found on Fragment."
    except Exception:
        pass
        
    return result


async def fetch_market(endpoint: str) -> list:
    url = f"https://fragment.com/{endpoint}"
    items = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    rows = soup.find_all("tr", class_="tm-row-selectable")
                    # STRICTLY TOP 5 items for the Image Cards
                    for row in rows[:5]:  
                        name_el = row.find("div", class_="table-cell-value tm-value")
                        price_el = row.find("div", class_="table-cell-value tm-value icon-before icon-ton")
                        
                        # Real Bids Extraction logic with "0" fallback
                        bids_text = "0"
                        for div in row.find_all("div"):
                            dt = div.get_text(strip=True).lower()
                            if "bid" in dt and "step" not in dt and "min" not in dt:
                                parts = dt.split()
                                if parts and parts[0].isdigit():
                                    bids_text = parts[0]
                                    break
                        
                        # Ends Extraction
                        ends_text = "Ended"
                        time_el = row.find("time")
                        if time_el:
                            ends_text = time_el.get_text(strip=True)
                        else:
                            for div in row.find_all("div", class_="table-cell-desc"):
                                dt = div.get_text(strip=True)
                                if "hour" in dt or "day" in dt or "minute" in dt or "second" in dt or "d " in dt or "h " in dt:
                                    ends_text = dt
                                    break
                        
                        items.append({
                            "name": name_el.get_text(strip=True) if name_el else "N/A",
                            "ends": ends_text,
                            "bids": bids_text,
                            "price": price_el.get_text(strip=True) if price_el else "0"
                        })
    except Exception:
        pass
        
    return items


async def fetch_similar(username: str) -> list:
    username = username.lower().replace("@", "").strip()
    url = f"https://fragment.com/usernames?query={username}"
    items = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    rows = soup.find_all("tr", class_="tm-row-selectable")
                    for row in rows[:5]:
                        name_el = row.find("div", class_="table-cell-value tm-value")
                        if not name_el: continue
                        
                        name = name_el.get_text(strip=True)
                        if not name.startswith("@"): name = f"@{name}"
                        
                        price_el = row.find("div", class_="table-cell-value tm-value icon-before icon-ton")
                        price = price_el.get_text(strip=True) if price_el else ""
                        
                        status_el = row.find(class_="tm-status-label")
                        status_text = status_el.get_text(strip=True).lower() if status_el else "unavailable"
                        
                        is_nft = False
                        display_status = "Non-NFT"
                        
                        if "sold" in status_text:
                            is_nft = True
                            display_status = "Sold"
                        elif "avail" in status_text:
                            is_nft = True
                            display_status = "Available"
                        elif "auction" in status_text:
                            is_nft = True
                            display_status = "On Auction"
                            
                        items.append({
                            "name": name,
                            "is_nft": is_nft,
                            "price": price,
                            "status": display_status
                        })
    except Exception:
        pass
        
    if not items:
        items.append({"name": f"@{username}", "is_nft": False, "price": "", "status": "Non-NFT"})
        
    return items


async def fetch_history(username: str) -> list:
    username = username.lower().replace("@", "").strip()
    url = f"https://fragment.com/username/{username}"
    history = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    rows = soup.find_all("tr")
                    for row in rows:
                        time_el = row.find("time")
                        if not time_el:
                            continue
                            
                        date_text = time_el.get_text(strip=True)
                        
                        wallets = row.find_all("a", class_="tm-wallet")
                        if wallets:
                            buyer_text = wallets[-1].get_text(strip=True)
                            history.append((date_text, buyer_text))
                            
    except Exception:
        pass
        
    return history[:5] if history else ["No history available."]


async def fetch_premium_packages() -> list:
    return [{"title": "3 Months", "price": "12.99 TON"}, {"title": "6 Months", "price": "19.99 TON"}, {"title": "1 Year", "price": "29.99 TON"}]

async def fetch_stars_packages() -> list:
    return [{"title": "50 Stars", "price": "0.15 TON"}, {"title": "250 Stars", "price": "0.75 TON"}, {"title": "1000 Stars", "price": "2.99 TON"}]
