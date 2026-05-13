import os
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs
from dotenv import load_dotenv

load_dotenv()

AFFILIATE_CONFIG = {
    "amazon": {"param": "tag", "id": os.getenv("AMAZON_AFF_ID", "dealpilot-20")},
    "ebay": {"param": "campid", "id": os.getenv("EBAY_AFF_ID", "5338000000")},
    "walmart": {"param": "affillinktype", "id": os.getenv("WALMART_AFF_ID", "10")},
    # Add BestBuy, Flipkart, AliExpress
}

def construct_affiliate_url(platform: str, raw_url: str) -> str:
    """Safely injects affiliate parameters into scraped URLs."""
    platform = platform.lower()
    if platform not in AFFILIATE_CONFIG:
        return raw_url
        
    config = AFFILIATE_CONFIG[platform]
    url_parts = list(urlparse(raw_url))
    query = parse_qs(url_parts[4])
    
    # Inject our affiliate ID
    query[config["param"]] = [config["id"]]
    
    url_parts[4] = urlencode(query, doseq=True)
    return urlunparse(url_parts)
