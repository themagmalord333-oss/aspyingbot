"""
# ==========================================
# Project: ANYSNAP
# Module: fragment/scraper.py
# ==========================================
"""

import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fragment.com/"
}

async def fetch_item_details(session, item_url, name, ends):
    """
    Deep Scraper: Opens actual item page to find TRUE Highest Bid and Bid History
    """
    price = "0"
    bids_count = "0"
    
    try:
        async with session.get(item_url, headers=HEADERS, timeout=10) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                
                # 1. FETCH REAL HIGHEST BID
                highest_lbl = soup.find(lambda t: t.name in ["div", "span"] and t.get_text(strip=True) == "Highest bid")
                if highest_lbl:
                    val_el = highest_lbl.find_next("div", class_=re.compile("tm-value|icon-ton"))
                    if val_el: price = val_el.get_text(strip=True)
                else:
                    # Fallback to Minimum bid ONLY if Highest bid is missing
                    min_lbl = soup.find(lambda t: t.name in ["div", "span"] and t.get_text(strip=True) == "Minimum bid")
                    if min_lbl:
                        val_el = min_lbl.find_next("div", class_=re.compile("tm-value|icon-ton"))
                        if val_el: price = val_el.get_text(strip=True)

                # 2. FETCH REAL BIDS COUNT FROM TABLE
                history_lbl = soup.find(lambda t: t.name in ["h2", "h3", "div"] and "Bid History" in t.get_text(strip=True))
                if history_lbl:
                    table = history_lbl.find_next("table")
                    if table:
                        rows = table.find_all("tr")
                        # Count rows that contain 'td' (skipping header 'th' rows)
                        data_rows = [r for r in rows if r.find("td")]
                        bids_count = str(len(data_rows))
                
                # 3. FALLBACK REGEX 
                if bids_count == "0":
                    page_text = soup.get_text(separator=" ").lower()
                    match = re.search(r'(\d+)\s*bids?', page_text)
                    if match:
                        bids_count = match.group(1)

    except Exception:
        pass
        
    return {
        "name": name,
        "ends": ends,
        "bids": bids_count,
        "price": price if price else "0"
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
    items = []
    
    # Check if this is a DOMAINS request (to append .t.me.ton to names like reference bot)
    is_domains = False
    if "domains" in endpoint:
        is_domains = True
        # Fragment doesn't have a domains endpoint anymore. 
        # The reference bot pulls top usernames and displays them as domains.
        endpoint = "usernames?sort=ending" 

    # URL OVERRIDE: Prevent 'Ending soon' spam filter for lists
    if endpoint == "numbers?sort=ending":
        endpoint = "numbers"
    elif endpoint == "usernames?sort=ending" and not is_domains:
        endpoint = "usernames"

    url = f"https://fragment.com/{endpoint}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    rows = soup.find_all("tr", class_="tm-row-selectable")
                    tasks = []
                    
                    for row in rows:
                        if ("numbers" in endpoint and len(items) >= 5) or ("numbers" not in endpoint and len(tasks) >= 5):
                            break

                        name_el = row.find("div", class_=re.compile("tm-value"))
                        name_val = name_el.get_text(strip=True) if name_el else "N/A"
                        
                        # Apply reference bot's Domain trick
                        if is_domains:
                            if name_val.startswith("@"):
                                name_val = name_val.replace("@", "") + ".t.me.ton"
                            else:
                                name_val = name_val + ".t.me.ton"

                        # STRICT ISOLATION FILTER
                        if "numbers" in endpoint and not name_val.startswith("+888"):
                            continue
                        if ("usernames" in endpoint or is_domains) and name_val.startswith("+888"):
                            continue

                        price_el = row.find("div", class_=re.compile("icon-before icon-ton"))
                        list_price = price_el.get_text(strip=True) if price_el else "0"
                        
                        ends_text = "Ended"
                        time_el = row.find("time")
                        if time_el:
                            ends_text = time_el.get_text(strip=True)
                        else:
                            for div in row.find_all("div", class_=re.compile("tm-desc|table-cell-desc")):
                                dt = div.get_text(strip=True).lower()
                                if any(x in dt for x in ["hour", "day", "minute", "second", "d ", "h ", "m "]):
                                    ends_text = div.get_text(strip=True)
                                    break
                                    
                        ends_formatted = ends_text.replace(" days", "d").replace(" day", "d")
                        ends_formatted = ends_formatted.replace(" hours", "h").replace(" hour", "h")
                        ends_formatted = ends_formatted.replace(" minutes", "m").replace(" minute", "m")
                        ends_formatted = ends_formatted.replace(" seconds", "s").replace(" second", "s")
                        
                        if "numbers" in endpoint or "usernames" in endpoint or is_domains:
                            if "s" in ends_formatted and "d" not in ends_formatted and "h" not in ends_formatted:
                                continue 
                            if "0s" in ends_formatted or ends_formatted == "Ended":
                                continue

                        # FAST LIST SCRAPE FOR NUMBERS
                        if "numbers" in endpoint:
                            items.append({
                                "name": name_val,
                                "ends": ends_formatted,
                                "bids": "0", 
                                "price": list_price
                            })
                            continue

                        # DEEP SCRAPE FOR USERNAMES / TRENDING / DOMAINS
                        link_el = row.find("a", class_="tm-row-link")
                        item_url = f"https://fragment.com{link_el['href']}" if link_el and 'href' in link_el.attrs else ""
                        if not item_url:
                            clean_name = name_val.replace("@", "").replace("+", "").replace(".t.me.ton", "").replace(" ", "")
                            item_url = f"https://fragment.com/username/{clean_name}"

                        tasks.append(fetch_item_details(session, item_url, name_val, ends_formatted))
                        
                    if tasks:
                        items = await asyncio.gather(*tasks)
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
