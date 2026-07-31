"""
# ==========================================
# Project: ANYSNAP
# Developer: Ziran ronal | MAGMAxRICH
# Module: fragment/scraper.py
# ==========================================
"""

import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def scrape_fragment(query: str, is_number: bool = False) -> str:
    """
    Scrapes Fragment.com for a Telegram username or number.
    Strictly returns the fetched data as a JSON object.
    """
    if is_number:
        # Format number by removing any '+' signs
        clean_query = query.replace("+", "").strip()
        url = f"https://fragment.com/number/{clean_query}"
        query_type = "number"
    else:
        # Format username by removing any '@' signs
        clean_query = query.replace("@", "").strip()
        url = f"https://fragment.com/username/{clean_query}"
        query_type = "username"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    # Default Result Structure (JSON ready)
    result = {
        "project": "ANYSNAP",
        "query": clean_query,
        "type": query_type,
        "status": "unknown",
        "price_ton": None,
        "availability": "Not Found / Error",
        "url": url
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # 1. Check Status / Availability
                    status_element = soup.find("div", class_="tm-section-header-status")
                    if status_element:
                        result["status"] = "success"
                        result["availability"] = status_element.text.strip()
                    
                    # 2. Check Price in TON (if it is on auction or sold)
                    price_element = soup.find("div", class_="table-cell-value tm-value icon-before icon-ton")
                    if price_element:
                        result["price_ton"] = price_element.text.strip()
                        
                elif response.status == 404:
                    result["status"] = "not_found"
                    result["availability"] = "Invalid or unavailable on Fragment"
                else:
                    result["status"] = f"error_{response.status}"
                    
    except asyncio.TimeoutError:
        result["status"] = "timeout"
        result["availability"] = "Connection to Fragment timed out"
    except Exception as e:
        result["status"] = "exception"
        result["availability"] = str(e)
        
    # Strictly return as a JSON string
    return json.dumps(result, indent=4)

# ==========================================
# Testing Block (Uncomment to test in Pydroid 3)
# ==========================================
# if __name__ == "__main__":
#     async def test():
#         # Test Username Search
#         print("Searching Username...")
#         username_json = await scrape_fragment("news")
#         print(username_json)
#         
#         print("\nSearching Number...")
#         # Test Number Search
#         number_json = await scrape_fragment("8888888", is_number=True)
#         print(number_json)
#         
#     asyncio.run(test())