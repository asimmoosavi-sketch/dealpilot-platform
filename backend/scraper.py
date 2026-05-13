import httpx
from bs4 import BeautifulSoup
import asyncio
from affiliate import construct_affiliate_url

# Anti-Bot Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

async def fetch_ebay(client, query):
    try:
        # Example Scraping Logic (eBay is usually the most lenient with scrapers)
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
        response = await client.get(url, headers=HEADERS, timeout=10.0)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        items = soup.select('.s-item__wrapper')[:3] # Get top 3
        for item in items:
            title = item.select_one('.s-item__title')
            price = item.select_one('.s-item__price')
            link = item.select_one('.s-item__link')
            img = item.select_one('.s-item__image-img')
            
            if title and price and link:
                raw_url = link['href']
                results.append({
                    "id": raw_url.split('?')[0][-10:], # Unique ID gen
                    "platform": "eBay",
                    "title": title.text.replace("New Listing", "").strip(),
                    "price": price.text.strip(),
                    "original": None, # Calculate or extract if available
                    "image": img['src'] if img else "https://dummyimage.com/400x400/f8fafc/1e3a8a.png&text=No+Image",
                    "url": construct_affiliate_url("ebay", raw_url)
                })
        return results
    except Exception as e:
        print(f"eBay Scrape Error: {e}")
        return []

async def get_live_search_results(query: str):
    # Asynchronously scrape multiple sites at the exact same time
    async with httpx.AsyncClient() as client:
        # Add Amazon, Walmart, etc., here as you build their specific parsers
        tasks = [fetch_ebay(client, query)] 
        results = await asyncio.gather(*tasks)
        
        # Flatten the list of lists
        flat_results = [item for sublist in results for item in sublist]
        return flat_results
