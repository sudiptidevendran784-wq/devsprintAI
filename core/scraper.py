"""
Advanced Web Scraper and Content Segmenter for MessageMatch Enterprise.
Extracts hero sections, body copy, footers/disclaimers, structured JSON-LD data, and media.
"""

import time
import json
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
from config import USER_AGENT, HEDGES

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

def clean_text(text: str) -> str:
    """Normalize whitespace and remove excessive line breaks."""
    return re.sub(r"\s+", " ", text or "").strip()

def extract_json_ld(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract Schema.org JSON-LD objects for prices, offers, and organizations."""
    json_ld_data = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            raw = script.string
            if raw:
                parsed = json.loads(raw.strip())
                if isinstance(parsed, list):
                    json_ld_data.extend(parsed)
                elif isinstance(parsed, dict):
                    json_ld_data.append(parsed)
        except Exception:
            continue
    return json_ld_data

def segment_page_sections(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Segment the page into logical zones:
    1. Above the fold (Hero / Header / First 300 words)
    2. Main body (Product details, features, FAQs)
    3. Fine print & Disclaimers (Footers, terms, asterisks, small text)
    """
    # 1. Fine print / Disclaimers
    footer_texts = []
    for tag in soup.find_all(["footer", "aside", "small"]):
        footer_texts.append(tag.get_text(" ", strip=True))
    
    # Also find classes containing disclaimer, terms, legal
    disclaimer_elements = soup.find_all(
        attrs={"class": re.compile(r"(disclaimer|legal|terms|conditions|fine-print|notes|footnote)", re.I)}
    )
    for el in disclaimer_elements:
        footer_texts.append(el.get_text(" ", strip=True))
    
    footer_content = clean_text(" ".join(footer_texts))

    # 2. Above the fold / Hero
    hero_texts = []
    for h in soup.find_all(["h1", "h2"]):
        hero_texts.append(h.get_text(" ", strip=True))
    
    hero_divs = soup.find_all(attrs={"class": re.compile(r"(hero|banner|headline|lead|intro|top-section)", re.I)})
    for hd in hero_divs[:3]:
        hero_texts.append(hd.get_text(" ", strip=True))
        
    above_fold = clean_text(" ".join(hero_texts))
    
    # 3. Full cleaned body (excluding scripts, styles)
    body_soup = BeautifulSoup(str(soup), "html.parser")
    for s in body_soup(["script", "style", "noscript", "svg"]):
        s.decompose()
        
    full_body = clean_text(body_soup.get_text(" ", strip=True))
    
    return {
        "above_the_fold": above_fold[:1500] if above_fold else full_body[:600],
        "footer_disclaimers": footer_content[:3000],
        "full_body": full_body
    }

def fetch_landing_page(url: str, timeout: int = 12) -> Dict[str, Any]:
    """
    Fetch and comprehensively parse landing page content and media.
    """
    start_time = time.time()
    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout)
        resp.raise_for_status()
        load_time_ms = int((time.time() - start_time) * 1000)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "load_time_ms": 0,
            "text": "",
            "sections": {},
            "images": [],
            "meta": {}
        }

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Metadata extraction
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    meta_desc = ""
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    if desc_tag and desc_tag.get("content"):
        meta_desc = desc_tag["content"].strip()
        
    og_title = ""
    og_title_tag = soup.find("meta", attrs={"property": "og:title"})
    if og_title_tag and og_title_tag.get("content"):
        og_title = og_title_tag["content"].strip()

    # Images collection
    images = []
    # 1. OG / Twitter hero image (highest priority)
    og_img = soup.find("meta", attrs={"property": "og:image"}) or soup.find("meta", attrs={"name": "twitter:image"})
    if og_img and og_img.get("content"):
        images.append(urljoin(url, og_img["content"].strip()))
        
    # 2. Main DOM images
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original") or ""
        if not src or src.startswith("data:") or src.lower().endswith(".svg"):
            continue
        # Skip small icons/sprites/logos
        low_src = src.lower()
        if any(w in low_src for w in ("icon", "sprite", "pixel", "tracking", "avatar", "badge", "analytics", "1x1")):
            continue
        # Skip tiny dimensions if declared
        w = img.get("width")
        h = img.get("height")
        try:
            if w and int(str(w).replace("px","")) < 120:
                continue
            if h and int(str(h).replace("px","")) < 120:
                continue
        except (ValueError, TypeError):
            pass
            
        full_img_url = urljoin(url, src)
        images.append(full_img_url)
        
    # De-duplicate while preserving order
    unique_images = list(dict.fromkeys(images))[:10]
    
    # Structured JSON-LD microdata
    json_ld = extract_json_ld(soup)
    
    # Page Sectioning
    sections = segment_page_sections(soup)
    
    full_text = f"{title}. {meta_desc}. {sections['full_body']}"
    
    return {
        "success": True,
        "error": None,
        "url": url,
        "status_code": resp.status_code,
        "load_time_ms": load_time_ms,
        "title": title,
        "meta_description": meta_desc,
        "og_title": og_title,
        "text": full_text,
        "sections": sections,
        "images": unique_images,
        "json_ld": json_ld
    }
