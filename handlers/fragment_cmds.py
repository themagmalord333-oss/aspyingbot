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
    url = f"https://fragment.com/username/{username}"
    
    result = {
        "username": username,
        "status": "Unknown",
        "ends_in": "",
        "highest_bid": "-",
        "bid_step": "-",
        "min_bid": "-",
        "usd_highest": "-",
        "usd_min": "-",
        "info_text": "This username is not available."
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Get Status
                    status_el = soup.find(class_="tm-section-header-status")
                    if status_el:
                        result["status"] = status_el.get_text(strip=True)
                    
                    if "Banned" in result["status"]:
                        result["info_text"] = "This username is banned and cannot be registered or purchased."
                    elif "Available" in result["status"]:
                        result["info_text"] = "This username is available for auction."
                        
                    # Get Time Left
                    time_el = soup.find("time")
                    if time_el:
                        result["ends_in"] = time_el.get_text(strip=True)

                    # Extract values (Very basic extraction for the UI)
                    values = soup.find_all("div", class_="table-cell-value tm-value icon-before icon-ton")
                    usd_values = soup.find_all("div", class_="table-cell-desc")

                    if "Auction" in result["status"] and len(values) >= 3:
                        result["highest_bid"] = values[0].get_text(strip=True)
                        result["bid_step"] = values[1].get_text(strip=True)
                        result["min_bid"] = values[2].get_text(strip=True)
                        
                        # Extracting USD approximate values
                        if len(usd_values) >= 3:
                            result["usd_highest"] = usd_values[0].get_text(strip=True).replace("~", "≈ ")
                            result["usd_min"] = usd_values[2].get_text(strip=True).replace("~", "≈ ")

                elif response.status == 404:
                    result["status"] = "Not Found"
                    result["info_text"] = "Username not found on Fragment."
    except Exception:
        pass
        
    return result

# You can keep your other functions (fetch_market, fetch_similar, etc.) here exactly as they were.
