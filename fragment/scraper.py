"""
# ==========================================
# Project: ANYSNAP
# Module: fragment/scraper.py
# ==========================================
"""

import asyncio
import aiohttp
import re
import time
from bs4 import BeautifulSoup

# Ultimate stealth headers to bypass Cloudflare Rate Limits & WAF
CHROME_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fragment.com/",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}

async def fetch_item_details(session, item_url, name, ends, list_price):
    """
    Deep Scraper: Safely opens the item page sequentially to bypass Cloudflare limits.
    Uses Regex to reliably extract Highest Bid and Bid History regardless of DOM changes.
    """
    price = list_price
    bids_count = "0"
    
    try:
        async with session.get(item_url, headers=CHROME_HEADERS, timeout=10) as resp:
            if resp.status == 200:
                html = await resp.text()
                
                # 1. EXTRACT REAL HIGHEST BID VIA REGEX
                hb_match = re.search(r'Highest bid.*?tm-value[^>]*>([^<]+)</div>', html, re.IGNORECASE | re.DOTALL)
                if hb_match:
                    parsed = hb_match.group(1).strip()
                    if parsed and parsed != "0": 
                        price = parsed
                else:
                    # Fallback to Minimum bid ONLY if Highest bid is missing
                    min_match = re.search(r'Minimum bid.*?tm-value[^>]*>([^<]+)</div>', html, re.IGNORECASE | re.DOTALL)
                    if min_match:
                        parsed = min_match.group(1).strip()
                        if parsed: 
                            price = parsed

                # 2. EXTRACT REAL BIDS COUNT FROM TABLE VIA REGEX
                history_match = re.search(r'Bid History.*?<table[^>]*>(.*?)</table>', html, re.IGNORECASE | re.DOTALL)
                if history_match:
                    table_html = history_match.group(1)
                    # Count data rows (td), ignore headers (th)
                    data_rows = re.findall(r'<tr[^>]*>.*?<td[^>]*>', table_html, re.IGNORECASE | re.DOTALL)
                    if data_rows:
                        bids_count = str(len(data_rows))
                
                # 3. TEXT FALLBACK
                if bids_count == "0":
                    bids_match = re.search(r'(\d+)\s*bids?', html, re.IGNORECASE)
                    if bids_match:
                        bids_count = bids_match.group(1)

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
            async with session.get(url, headers=CHROME_HEADERS, timeout=10) as response:
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
    
    # URL Overrides
    if endpoint == "numbers?sort=ending":
        endpoint = "numbers"
    elif endpoint == "usernames?sort=ending":
        endpoint = "usernames"

    # ========================================================================
    # 1. DOMAINS ISOLATION (TonAPI - PERFECTLY UNTOUCHED)
    # ========================================================================
    if "domains" in endpoint:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://tonapi.io/v2/dns/auctions", timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        auctions = data.get("data", data.get("auctions", []))
                        if not auctions and isinstance(data, list):
                            auctions = data
                            
                        valid_auctions = []
                        for auc in auctions:
                            domain = auc.get("domain", auc.get("name", ""))
                            if domain.endswith(".ton") and not domain.endswith(".t.me.ton"):
                                valid_auctions.append(auc)
                                
                        valid_auctions = sorted(valid_auctions, key=lambda x: int(x.get("price", x.get("amount", x.get("highest_bid", 0)))), reverse=True)
                            
                        for auc in valid_auctions[:5]:
                            domain = auc.get("domain", auc.get("name", "Unknown.ton"))
                            if len(domain) > 20: domain = domain[:17] + "..."
                            
                            price_raw = auc.get("price", auc.get("amount", auc.get("highest_bid", 0)))
                            if price_raw:
                                p_float = float(price_raw) / 1e9
                                price = str(int(p_float)) if p_float.is_integer() else f"{p_float:.2f}"
                            else:
                                price = "0"
                            
                            bids = str(auc.get("bids", auc.get("bidCount", auc.get("bids_count", 0))))
                            
                            ends_text = "Active"
                            end_time = auc.get("date", auc.get("endTime", auc.get("end_time", 0)))
                            if end_time:
                                remaining = int(end_time) - int(time.time())
                                if remaining > 0:
                                    d = remaining // 86400
                                    h = (remaining % 86400) // 3600
                                    m = (remaining % 3600) // 60
                                    if d > 0: ends_text = f"{d}d {h}h"
                                    elif h > 0: ends_text = f"{h}h {m}m"
                                    else: ends_text = f"{m}m"
                                else:
                                    ends_text = "Ended"
                                    
                            items.append({
                                "name": domain,
                                "ends": ends_text,
                                "bids": bids,
                                "price": price
                            })
                        return items
        except Exception:
            pass
        return items

    # ========================================================================
    # 2. FRAGMENT AUCTIONS (Usernames, Numbers, Trending, Floor)
    # ========================================================================
    url = f"https://fragment.com/{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=CHROME_HEADERS, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    rows = soup.find_all("tr", class_="tm-row-selectable")
                    to_fetch = []
                    
                    for row in rows:
                        if ("numbers" in endpoint and len(items) >= 5) or ("numbers" not in endpoint and len(to_fetch) >= 5):
                            break

                        name_el = row.find("div", class_=re.compile("tm-value"))
                        name_val = name_el.get_text(strip=True) if name_el else "N/A"
                        
                        # Strict Type Isolation
                        if "numbers" in endpoint and not name_val.startswith("+888"):
                            continue
                        if "usernames" in endpoint and name_val.startswith("+888"):
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
                        
                        if "numbers" in endpoint or "usernames" in endpoint:
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

                        # PREPARE DEEP SCRAPE TARGETS FOR USERNAMES / TRENDING
                        link_el = row.find("a", class_="tm-row-link")
                        item_url = f"https://fragment.com{link_el['href']}" if link_el and 'href' in link_el.attrs else ""
                        if not item_url:
                            clean_name = name_val.replace("@", "").replace("+", "").replace(" ", "")
                            item_url = f"https://fragment.com/username/{clean_name}"

                        to_fetch.append({
                            "url": item_url,
                            "name": name_val,
                            "ends": ends_formatted,
                            "list_price": list_price
                        })
                        
                    # SEQUENTIAL FETCHING FIX (Bypasses Cloudflare 429 Anti-Bot Limits)
                    for req in to_fetch:
                        item_data = await fetch_item_details(session, req['url'], req['name'], req['ends'], req['list_price'])
                        items.append(item_data)
                        await asyncio.sleep(0.3)  # Human-like delay to prevent block
    except Exception:
        pass
        
    return items


async def fetch_similar(username: str) -> list:
    username = username.lower().replace("@", "").strip()
    url = f"https://fragment.com/usernames?query={username}"
    items = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=CHROME_HEADERS, timeout=10) as response:
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
            async with session.get(url, headers=CHROME_HEADERS, timeout=10) as response:
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
