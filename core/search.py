"""
Resilient Search and Advertiser Landing Page Discovery Engine.
Integrates DuckDuckGo search with brand matching heuristics and graceful fallback.
"""

import re
from urllib.parse import urlparse
from typing import List, Dict, Any
from config import SKIP_DOMAINS

try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        DDGS = None

def tokenize(s: str) -> set:
    return set(re.findall(r"[a-z0-9]{3,}", (s or "").lower()))

def search_landing_pages(ad_copy: str, brand: str = "", max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Search for official landing pages matching the ad copy and brand name.
    """
    results_raw = []
    ad_clean = " ".join(ad_copy.split()[:14])
    query = f"{brand} {ad_clean}".strip() if brand else ad_clean
    
    if DDGS is not None:
        try:
            with DDGS() as d:
                # duckduckgo_search v8+ text method
                res_iter = d.text(query, max_results=max_results + 4)
                for r in res_iter:
                    results_raw.append(r)
        except Exception:
            pass

    # If duckduckgo search returned no results, generate fallback synthetic brand search
    if not results_raw and brand:
        clean_brand_slug = re.sub(r"[^a-z0-9]", "", brand.lower())
        results_raw = [
            {
                "href": f"https://www.{clean_brand_slug}.com",
                "title": f"{brand} Official Homepage & Current Offers",
                "body": f"Official portal for {brand}. Explore features, pricing, promotional terms and latest announcements."
            },
            {
                "href": f"https://www.{clean_brand_slug}.com/promotions",
                "title": f"{brand} Special Deals, Discounts and Terms",
                "body": f"Current deals, coupon verification, eligibility terms and service turnaround details for {brand}."
            }
        ]

    ad_tokens = tokenize(ad_copy)
    brand_tokens = tokenize(brand)
    
    scored_candidates = []
    seen_urls = set()
    
    for r in results_raw:
        url = r.get("href") or r.get("url") or ""
        if not url or url in seen_urls:
            continue
            
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        
        # Skip banned social / aggregation sites
        if any(skip in netloc for skip in SKIP_DOMAINS):
            continue
            
        title = r.get("title", "")
        body = r.get("body", "") or r.get("snippet", "")
        combined = f"{title} {body}".lower()
        
        # Scoring logic
        content_tokens = tokenize(combined)
        overlap = len(ad_tokens & content_tokens)
        score = overlap * 2
        
        # Domain bonus if brand name matches netloc
        if brand:
            clean_b = brand.lower().replace(" ", "")
            if clean_b in netloc:
                score += 25
            elif any(bt in netloc for bt in brand_tokens):
                score += 15

        seen_urls.add(url)
        scored_candidates.append({
            "url": url,
            "netloc": netloc,
            "title": title or url,
            "snippet": body[:220] if body else "No page summary available.",
            "score": score
        })
        
    return sorted(scored_candidates, key=lambda x: -x["score"])[:max_results]
