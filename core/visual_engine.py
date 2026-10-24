"""
Visual Consistency and Multimodal Image Comparison Engine.
Performs perceptual hashing, dominant color extraction, chromatic harmony, and OCR extraction.
"""

import io
import base64
import math
from typing import List, Tuple, Dict, Any, Optional
import requests
from PIL import Image, ImageStat
from config import USER_AGENT

def download_image(url: str, timeout: int = 6) -> Optional[Image.Image]:
    """Download an image URL into a Pillow RGB Image object."""
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        return img
    except Exception:
        return None

def image_to_base64_thumb(img: Image.Image, size: Tuple[int, int] = (160, 160)) -> str:
    """Generate lightweight JPEG data-URI for dataframe or UI previews."""
    try:
        im = img.copy()
        im.thumbnail(size)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=82)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""

def dhash(img: Image.Image, n: int = 8) -> List[bool]:
    """Compute difference hash (dHash) for structural gradients."""
    g = img.convert("L").resize((n + 1, n), Image.Resampling.LANCZOS)
    px = list(g.getdata())
    bits = []
    for row in range(n):
        for col in range(n):
            bits.append(px[row * (n + 1) + col] > px[row * (n + 1) + col + 1])
    return bits

def ahash(img: Image.Image, n: int = 8) -> List[bool]:
    """Compute average hash (aHash) for luminance distribution."""
    g = img.convert("L").resize((n, n), Image.Resampling.LANCZOS)
    px = list(g.getdata())
    avg = sum(px) / len(px)
    return [p > avg for p in px]

def visual_similarity(a: Image.Image, b: Image.Image) -> int:
    """
    Combined visual similarity percentage (dHash + aHash).
    """
    try:
        da, db = dhash(a), dhash(b)
        aa, ab = ahash(a), ahash(b)
        d_sim = sum(x == y for x, y in zip(da, db)) / len(da)
        a_sim = sum(x == y for x, y in zip(aa, ab)) / len(aa)
        combined = (d_sim * 0.6) + (a_sim * 0.4)
        return round(combined * 100)
    except Exception:
        return 0

def extract_dominant_colors(img: Image.Image, num_colors: int = 4) -> List[Dict[str, Any]]:
    """
    Extract the top dominant colors from an image using quantization.
    Returns RGB tuple, hex representation, and frequency percentage.
    """
    try:
        im = img.copy().resize((120, 120))
        # Quantize down to reduced palette
        quantized = im.quantize(colors=num_colors)
        palette = quantized.getpalette()[:num_colors * 3]
        
        # Color counts
        counts = quantized.getcolors()
        total_pixels = sum(c[0] for c in counts)
        
        colors = []
        for count, idx in sorted(counts, key=lambda x: -x[0])[:num_colors]:
            r = palette[idx * 3]
            g = palette[idx * 3 + 1]
            b = palette[idx * 3 + 2]
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            pct = round((count / total_pixels) * 100, 1)
            colors.append({"rgb": (r, g, b), "hex": hex_code, "percent": pct})
        return colors
    except Exception:
        return [{"rgb": (80, 80, 80), "hex": "#505050", "percent": 100.0}]

def calculate_color_harmony_score(palette_a: List[Dict[str, Any]], palette_b: List[Dict[str, Any]]) -> int:
    """
    Calculate color consistency between ad creative and landing page hero.
    Evaluates minimal Euclidean distance in RGB color space.
    """
    if not palette_a or not palette_b:
        return 70  # Neutral baseline
    
    total_dist = 0
    comparisons = 0
    for ca in palette_a[:3]:
        r1, g1, b1 = ca["rgb"]
        min_dist = float("inf")
        for cb in palette_b[:3]:
            r2, g2, b2 = cb["rgb"]
            dist = math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
            if dist < min_dist:
                min_dist = dist
        total_dist += min_dist
        comparisons += 1
    
    avg_dist = total_dist / max(1, comparisons)
    # Maximum possible distance is sqrt(255^2 * 3) ~ 441.7
    harmony = max(0, min(100, round((1.0 - (avg_dist / 441.7)) * 100)))
    return harmony

def extract_ocr_text(img: Image.Image) -> Dict[str, Any]:
    """
    Extract text from ad image using pytesseract if available.
    Provides clear error reporting when OCR binary is uninstalled.
    """
    try:
        import pytesseract
        text = pytesseract.image_to_string(img).strip()
        return {
            "success": True,
            "text": text,
            "engine": "pytesseract",
            "message": "Extracted text via OCR successfully."
        }
    except ImportError:
        return {
            "success": False,
            "text": "",
            "engine": "none",
            "message": "pytesseract package is not installed."
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "engine": "pytesseract",
            "message": f"Tesseract binary not found on system: {e}"
        }
