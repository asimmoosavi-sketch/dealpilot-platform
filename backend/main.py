from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, constr
from scraper import get_live_search_results
import re

# Initialize Rate Limiter (Prevents DDoS and Abuse)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="DealPilot API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Security (Only allow your Render frontend to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dealpilot-31p0.onrender.com", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Secure Input Validation (Prevents XSS / SQL Injection)
def sanitize_query(q: str):
    sanitized = re.sub(r'[^\w\s-]', '', q) # Only allow alphanumeric, spaces, and hyphens
    return sanitized.strip()

@app.get("/api/search")
@limiter.limit("15/minute") # Strict rate limiting to prevent scraping of your API
async def search_deals(request: Request, q: str = Query(..., min_length=2, max_length=50)):
    clean_query = sanitize_query(q)
    if not clean_query:
        raise HTTPException(status_code=400, detail="Invalid search query.")
    
    # Fetch live data via our custom scraper
    results = await get_live_search_results(clean_query)
    return {"query": clean_query, "status": "success", "data": results}

@app.get("/api/autocomplete")
@limiter.limit("40/minute")
async def autocomplete(request: Request, q: str = Query(..., min_length=2)):
    # Returns quick suggestions for the dropdown
    clean_query = sanitize_query(q)
    return {"suggestions": [f"{clean_query} pro", f"{clean_query} max", f"best {clean_query} deals"]}

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
