"""
Ad Creative Mockups and Multimodal Visual Palette Comparison Views.
"""

import html
from typing import List, Dict, Any

def render_ad_mockup(ad_format: str, brand: str, ad_copy: str, landing_url: str) -> str:
    brand_esc = html.escape(brand or "Brand Name")
    ad_esc = html.escape(ad_copy)
    url_esc = html.escape(landing_url or "https://example.com/offer")
    
    if ad_format == "Google Search":
        return f"""
        <div style="border: 1px solid #dadce0; border-radius: 8px; padding: 14px 16px; background: #ffffff;
                    font-family: Roboto, Arial, sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <span style="font-size: 11px; font-weight: 700; color: #202124; background: #f1f3f4;
                             padding: 1px 6px; border-radius: 3px;">Sponsored</span>
                <span style="font-size: 12px; color: #202124;">{url_esc[:45]}</span>
            </div>
            <div style="font-size: 17px; font-weight: 500; color: #1a0dab; margin-bottom: 4px; cursor: pointer;">
                {brand_esc} | Official Site & Special Promotion
            </div>
            <div style="font-size: 13px; color: #4d5156; line-height: 1.45;">
                {ad_esc}
            </div>
            <div style="display: flex; gap: 14px; margin-top: 10px; font-size: 12px; color: #1a0dab;">
                <span>&bull; View Pricing & Terms</span>
                <span>&bull; Customer Reviews</span>
                <span>&bull; Instant Application</span>
            </div>
        </div>
        """
    else:  # Meta / Instagram Feed
        return f"""
        <div style="border: 1px solid #e5e7eb; border-radius: 12px; background: #ffffff;
                    overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.06); font-family: -apple-system, sans-serif;">
            <div style="display: flex; align-items: center; gap: 10px; padding: 10px 14px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #4f46e5;
                            color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;">
                    {brand_esc[:1]}
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 13px; color: #111827;">{brand_esc}</div>
                    <div style="font-size: 11px; color: #6b7280;">Sponsored &bull; 🌐</div>
                </div>
            </div>
            <div style="padding: 0 14px 10px 14px; font-size: 13px; color: #1f2937; line-height: 1.4;">
                {ad_esc}
            </div>
            <div style="background: #f9fafb; border-top: 1px solid #f3f4f6; padding: 10px 14px;
                        display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #6b7280;">{url_esc[:30]}</div>
                    <div style="font-size: 13px; font-weight: 700; color: #111827;">Exclusive Online Offer</div>
                </div>
                <div style="background: #e5e7eb; color: #111827; padding: 5px 12px; border-radius: 6px;
                            font-size: 12px; font-weight: 600;">
                    Learn More
                </div>
            </div>
        </div>
        """

def render_color_palette_comparison(ad_palette: List[Dict[str, Any]], page_palette: List[Dict[str, Any]], harmony_score: int) -> str:
    ad_swatches = ""
    for c in ad_palette[:4]:
        hex_c = c.get("hex", "#505050")
        pct = c.get("percent", 25.0)
        ad_swatches += f"""
        <div style="display: inline-block; text-align: center; margin-right: 8px;">
            <div style="width: 38px; height: 38px; border-radius: 8px; background: {hex_c};
                        box-shadow: 0 2px 4px rgba(0,0,0,0.15); border: 1px solid rgba(0,0,0,0.1);"></div>
            <div style="font-size: 10px; font-weight: 600; color: #475569; margin-top: 4px;">{hex_c}</div>
        </div>
        """
        
    page_swatches = ""
    for c in page_palette[:4]:
        hex_c = c.get("hex", "#505050")
        pct = c.get("percent", 25.0)
        page_swatches += f"""
        <div style="display: inline-block; text-align: center; margin-right: 8px;">
            <div style="width: 38px; height: 38px; border-radius: 8px; background: {hex_c};
                        box-shadow: 0 2px 4px rgba(0,0,0,0.15); border: 1px solid rgba(0,0,0,0.1);"></div>
            <div style="font-size: 10px; font-weight: 600; color: #475569; margin-top: 4px;">{hex_c}</div>
        </div>
        """
        
    h_color = "#16a34a" if harmony_score >= 70 else ("#f59e0b" if harmony_score >= 50 else "#dc2626")

    return f"""
    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 18px; background: #ffffff; margin-top: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 13px; color: #334155;">Chromatic Coherence & Palette Alignment</span>
            <span style="background: {h_color}; color: #ffffff; font-weight: 700; font-size: 11px;
                         padding: 2px 10px; border-radius: 999px;">{harmony_score}% Harmony</span>
        </div>
        <div style="display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap;">
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #64748b; margin-bottom: 6px;">AD CREATIVE PALETTE</div>
                {ad_swatches or "<small>No image uploaded</small>"}
            </div>
            <div>
                <div style="font-size: 11px; font-weight: 600; color: #64748b; margin-bottom: 6px;">LANDING PAGE HERO PALETTE</div>
                {page_swatches or "<small>No hero images found</small>"}
            </div>
        </div>
    </div>
    """
