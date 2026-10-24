"""
Google Ads Quality Score and Meta Ad Relevance Diagnostic Estimator.
Simulates ad network auction impact, predicted CPC discount/penalty, and estimated ROI efficiency.
"""

from typing import Dict, Any

def estimate_quality_score(
    claim_score: int,
    visual_score: int,
    compliance_score: int,
    load_time_ms: int = 450,
    has_above_fold_hero_match: bool = True
) -> Dict[str, Any]:
    """
    Simulate Google Ads Quality Score (1 to 10) and Meta Relevance Diagnostics.
    """
    # Weighted component scoring
    speed_factor = 1.0 if load_time_ms < 800 else (0.8 if load_time_ms < 2000 else 0.5)
    hero_factor = 1.05 if has_above_fold_hero_match else 0.85
    
    composite_pct = (
        (claim_score * 0.45) +
        (visual_score * 0.20) +
        (compliance_score * 0.20) +
        (speed_factor * 100 * 0.15)
    ) * (hero_factor)
    
    composite_pct = max(10, min(100, composite_pct))
    
    # Map composite (10-100) to Quality Score (1-10)
    qs = round(composite_pct / 10.0)
    qs = max(1, min(10, qs))
    
    # CPC impact curve based on industry benchmark data
    # (Google Ads Quality Score vs Average CPC variation)
    cpc_impact_table = {
        10: -50.0,
        9: -37.5,
        8: -25.0,
        7: 0.0,    # Benchmark baseline
        6: +16.7,
        5: +28.5,
        4: +67.3,
        3: +150.0,
        2: +250.0,
        1: +400.0
    }
    cpc_impact_pct = cpc_impact_table.get(qs, 0.0)
    
    # Meta Relevance Diagnostics
    if qs >= 8:
        meta_quality = "Above Average (Top 20%)"
        meta_conversion = "Above Average"
        status_verdict = "Optimal Auction Advantage"
        status_color = "#16a34a"
    elif qs >= 6:
        meta_quality = "Average"
        meta_conversion = "Average"
        status_verdict = "Acceptable Performance"
        status_color = "#f59e0b"
    elif qs >= 4:
        meta_quality = "Below Average (Bottom 35%)"
        meta_conversion = "Below Average (Bottom 20%)"
        status_verdict = "Significant CPC Surcharge"
        status_color = "#ea580c"
    else:
        meta_quality = "Below Average (Bottom 10%)"
        meta_conversion = "Below Average (Bottom 10%)"
        status_verdict = "Severe Ad Suppression Risk"
        status_color = "#dc2626"

    # Financial impact model based on $10k monthly spend baseline
    monthly_budget = 10000.0
    monthly_waste = 0.0
    if cpc_impact_pct > 0:
        monthly_waste = round(monthly_budget * (cpc_impact_pct / (100 + cpc_impact_pct)))
    
    return {
        "quality_score": qs,
        "composite_pct": round(composite_pct, 1),
        "cpc_impact_pct": cpc_impact_pct,
        "monthly_waste_est": monthly_waste,
        "meta_quality_ranking": meta_quality,
        "meta_conversion_ranking": meta_conversion,
        "status_verdict": status_verdict,
        "status_color": status_color,
        "page_speed_rating": "Fast (<800ms)" if load_time_ms < 800 else ("Moderate" if load_time_ms < 2000 else "Slow (>2s)")
    }
