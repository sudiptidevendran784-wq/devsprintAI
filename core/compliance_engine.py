"""
Regulatory, FTC Compliance, and Dark Pattern Screening Engine.
Identifies regulatory risks, deceptive urgency, hidden recurring billing, and missing disclosures.
"""

import re
from typing import List, Dict, Any, Tuple
from config import REGULATORY_PATTERNS

def audit_compliance_risks(ad_copy: str, page_text: str, footer_text: str = "") -> List[Dict[str, Any]]:
    """
    Screen the ad and landing page pair against regulatory compliance and dark pattern rules.
    """
    findings = []
    
    # 1. Deceptive Urgency / Artificial Scarcity
    ad_urgency = re.findall(REGULATORY_PATTERNS["Deceptive Urgency"], ad_copy, re.I)
    page_urgency = re.findall(REGULATORY_PATTERNS["Deceptive Urgency"], page_text, re.I)
    if ad_urgency and not page_urgency:
        findings.append({
            "framework": "FTC Truth-in-Advertising / Dark Patterns",
            "type": "Unsubstantiated Urgency",
            "severity": "High",
            "trigger": ", ".join(set(ad_urgency)),
            "finding": "Ad uses artificial scarcity cues ('only few left', 'hurry') with zero inventory counter or scarcity signal on the landing page.",
            "recommendation": "Remove false urgency countdowns from ad creatives unless backed by real-time inventory API sync."
        })

    # 2. Hidden Negative Option / Auto-Renewal Traps
    has_free_in_ad = bool(re.search(r"\bfree (?:trial|sample|month|first month)\b", ad_copy, re.I))
    has_autorenew_in_page = bool(re.search(REGULATORY_PATTERNS["Hidden Auto-Renewal"], page_text + " " + footer_text, re.I))
    requires_cc = bool(re.search(r"\bcredit card required\b|\bauto[- ]charges\b|\bbilled after trial\b", page_text + " " + footer_text, re.I))
    
    if has_free_in_ad and has_autorenew_in_page:
        findings.append({
            "framework": "FTC Negative Option Rule (16 CFR Part 425)",
            "type": "Hidden Subscription Continuity",
            "severity": "Critical",
            "trigger": "Ad says 'Free Trial' while page enforces recurring auto-billing.",
            "finding": "The ad presents an offer as 'Free' without prominent upfront disclosure that a paid recurring subscription commences thereafter.",
            "recommendation": "Add explicit immediate disclosure: 'Renews automatically at $X/month after trial. Cancel anytime in 1 click.'"
        })

    # 3. Asterisk & Disclaimer Ambiguity
    ad_has_asterisk = "*" in ad_copy
    page_has_asterisk = "*" in page_text
    if ad_has_asterisk:
        if not footer_text and not page_has_asterisk:
            findings.append({
                "framework": "ASCI & Better Business Bureau Guidelines",
                "type": "Missing Asterisk Disclosures",
                "severity": "High",
                "trigger": "Ad features '*' conditional asterisk without landing page definition.",
                "finding": "Asterisks placed on pricing or claims in the ad are not explained above the fold or in terms.",
                "recommendation": "Provide explicit qualification footnote immediately legible beneath the matching headline."
            })

    # 4. Unsubstantiated Health / Cure Claims
    health_ad = re.findall(REGULATORY_PATTERNS["Unsubstantiated Health Claim"], ad_copy, re.I)
    if health_ad:
        has_fda_disclaimer = bool(re.search(r"\bnot evaluated by the fda\b|\bnot intended to diagnose, treat, cure\b", page_text + " " + footer_text, re.I))
        if not has_fda_disclaimer:
            findings.append({
                "framework": "FDA / FTC Dietary Supplement & Health Advertising Guidelines",
                "type": "Unqualified Medical/Health Claim",
                "severity": "Critical",
                "trigger": ", ".join(set(health_ad)),
                "finding": "Ad promises health breakthroughs ('cure', 'prevents disease') without mandatory statutory DSHEA disclaimer.",
                "recommendation": "Ensure mandatory FDA/DSHEA disclaimer is placed prominently wherever wellness claims appear."
            })

    # 5. Unsubstantiated Superlatives
    superlatives = re.findall(r"\b(#1|rated #?1|world's best|guaranteed lowest price|cheapest in market)\b", ad_copy, re.I)
    if superlatives:
        has_citation = bool(re.search(r"\baccording to\b|\bsource:|\bresearch by\b|\baudited by\b|\bbased on\b", page_text, re.I))
        if not has_citation:
            findings.append({
                "framework": "FTC Deceptive Advertising Guidelines",
                "type": "Unsubstantiated Superlative",
                "severity": "Medium",
                "trigger": ", ".join(set(superlatives)),
                "finding": f"Ad uses absolute superlative ('{superlatives[0]}') without independent citation or verifiable study citation.",
                "recommendation": "Attach credible third-party study source or rephrase to consumer sentiment ('Over 10,000 5-star reviews')."
            })

    return findings

def compute_compliance_score(findings: List[Dict[str, Any]]) -> int:
    """Calculate regulatory compliance score 0-100 based on detected infraction penalties."""
    if not findings:
        return 100
        
    penalties = {
        "Critical": 35,
        "High": 20,
        "Medium": 10,
        "Low": 5
    }
    total_penalty = sum(penalties.get(f.get("severity", "Medium"), 15) for f in findings)
    score = max(0, 100 - total_penalty)
    return score
