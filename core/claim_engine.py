"""
Advanced Multi-Category Claim and Offer Deadline Verification Engine.
Analyzes ad claims, verifies against landing page zones, and calculates discrepancy severity.
"""

import re
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from dateutil import parser as dparser
from config import CLAIM_RULES, HEDGES

# Date and deadline parsing constants
MONTHS = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_P = (rf"(?:{MONTHS}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?"
          rf"|\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTHS}\.?(?:,?\s+\d{{4}})?"
          rf"|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}})")
CUE_P = r"(?:offer\s+)?(?:ends?|ending|expires?|valid\s+(?:till|until|through|thru)|until|till|through|last day|validity)(?:\s+on)?"
DEADLINE_RE = re.compile(rf"({CUE_P})\s+({DATE_P})", re.I)
RELATIVE_RE = re.compile(
    r"(?:ends?|expires?|valid)\s+(?:today|tonight|tomorrow|this\s+\w+|in\s+\d+\s+(?:hours?|days?))"
    r"|limited[- ]time|last chance|while (?:stocks?|supplies) last|hurry|flash sale", re.I)

def tokenize(text: str) -> set:
    """Extract lowercase alpha-numeric tokens >= 3 chars."""
    return set(re.findall(r"[a-z0-9]{3,}", (text or "").lower()))

def extract_sentences(text: str) -> List[str]:
    """Segment text into individual sentences."""
    return [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", text or "") if len(s.strip()) > 12]

def find_best_evidence_sentence(claim: str, sentences: List[str]) -> Tuple[str, int]:
    """Find the sentence in a collection that best matches the claim tokens."""
    claim_tokens = tokenize(claim)
    if not claim_tokens:
        return "", 0
    best_sent = ""
    max_score = 0
    for s in sentences:
        s_tokens = tokenize(s)
        overlap = len(claim_tokens & s_tokens)
        if overlap > max_score:
            best_sent = s
            max_score = overlap
    return best_sent[:280], max_score

def parse_deadline_date(txt: str) -> Optional[date]:
    """Parse dates with ordinal removal and default handling."""
    cleaned = re.sub(r"(\d)(st|nd|rd|th)", r"\1", txt, flags=re.I).strip()
    try:
        return dparser.parse(
            cleaned,
            dayfirst=True,
            default=datetime(date.today().year, 1, 1)
        ).date()
    except (ValueError, OverflowError):
        return None

def analyze_claims(
    ad_copy: str,
    page_text: str,
    sections: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Perform deep verification of all claims made in the advertisement against the landing page.
    """
    if sections is None:
        sections = {"above_the_fold": page_text[:600], "footer_disclaimers": "", "full_body": page_text}

    rows = []
    page_sents = extract_sentences(page_text)
    above_sents = extract_sentences(sections.get("above_the_fold", ""))
    footer_sents = extract_sentences(sections.get("footer_disclaimers", ""))
    
    clean_page_lower = re.sub(r"\s+", " ", page_text.lower()).strip()
    clean_above_lower = re.sub(r"\s+", " ", sections.get("above_the_fold", "").lower()).strip()
    clean_footer_lower = re.sub(r"\s+", " ", sections.get("footer_disclaimers", "").lower()).strip()

    # 1. Standard Category Rules
    for category, meta in CLAIM_RULES.items():
        pattern = meta["pattern"]
        severity_base = meta["severity"]

        for m in re.finditer(pattern, ad_copy, re.I):
            claim = m.group(0).strip()
            norm_claim = re.sub(r"\s+", " ", claim.lower()).strip()

            ev_sentence, ev_score = find_best_evidence_sentence(claim, page_sents)
            
            # Location checks
            in_above_fold = norm_claim in clean_above_lower
            in_full_page = norm_claim in clean_page_lower
            in_footer = norm_claim in clean_footer_lower

            # Determine match status and zone
            if in_above_fold:
                status = "Supported (Hero)"
                location = "Above the Fold"
                severity = "Pass"
                evidence = ev_sentence or f"Direct prominent match found in headline/hero section."
            elif in_full_page:
                # Check if qualified by hedges
                is_hedged = any(h in ev_sentence.lower() for h in HEDGES) if ev_sentence else False
                if is_hedged:
                    status = "Qualified / Hedged"
                    location = "Main Body"
                    severity = "Medium"
                    evidence = f"Condition detected: \"{ev_sentence}\""
                else:
                    status = "Supported (Body)"
                    location = "Main Body"
                    severity = "Pass"
                    evidence = ev_sentence or "Found in landing page body copy."
            elif in_footer or (ev_score > 0 and any(norm_claim in fs.lower() for fs in footer_sents)):
                status = "Buried in Fine Print"
                location = "Footer / Disclaimers"
                severity = "High"
                evidence = f"Claim only disclosed in fine print: \"{ev_sentence}\""
            elif ev_sentence and ev_score >= max(1, len(tokenize(claim)) // 2):
                # Partial semantic match
                is_hedged = any(h in ev_sentence.lower() for h in HEDGES)
                if is_hedged:
                    status = "Not explicitly supported"
                    location = "Main Body"
                    severity = "High"
                    evidence = f"Conditional statement on page: \"{ev_sentence}\""
                else:
                    status = "Partial Match"
                    location = "Main Body"
                    severity = "Medium"
                    evidence = f"Related wording: \"{ev_sentence}\""
            else:
                status = "Not found on page"
                location = "Missing"
                severity = severity_base
                evidence = "No corresponding verification or proof found anywhere on the landing page."

            rows.append({
                "Category": category,
                "Claim": claim,
                "Status": status,
                "Location": location,
                "Severity": severity,
                "Evidence": evidence
            })

    # 2. Offer Deadlines & Urgency
    today = date.today()
    page_cue_dates = {parse_deadline_date(m.group(2)) for m in DEADLINE_RE.finditer(page_text)} - {None}
    page_any_dates = {parse_deadline_date(m.group(0)) for m in re.finditer(DATE_P, page_text, re.I)} - {None}

    for m in DEADLINE_RE.finditer(ad_copy):
        d = parse_deadline_date(m.group(2))
        if not d:
            continue
        claim = m.group(0).strip()
        
        if d in page_cue_dates or d in page_any_dates:
            status = "Supported (Date Match)"
            severity = "Pass"
            evidence = f"Landing page explicitly confirms validity date {d.strftime('%d %b %Y')}."
        elif page_cue_dates:
            status = "Date Mismatch"
            severity = "Critical"
            evidence = "Landing page states different expiration: " + ", ".join(f"{x.strftime('%d %b %Y')}" for x in sorted(page_cue_dates))
        else:
            status = "Not found on page"
            severity = "High"
            evidence = "No offer deadline found on the landing page. Users may doubt promotion legitimacy."

        if d < today:
            status = "Expired"
            severity = "Critical"
            evidence += f" ⚠️ CRITICAL: Expiration date ({d.strftime('%d %b %Y')}) has already passed!"

        rows.append({
            "Category": "Offer Deadline",
            "Claim": claim,
            "Status": status,
            "Location": "Landing Page Dates",
            "Severity": severity,
            "Evidence": evidence
        })

    # 3. Relative Urgency Clauses
    for m in RELATIVE_RE.finditer(ad_copy):
        claim = m.group(0).strip()
        urgency_found = re.search(r"\b(limited[- ]time|ends?|expires?|stock|hurry|flash|hours left)\b", page_text, re.I)
        if urgency_found:
            status = "Urgency Reflected"
            severity = "Pass"
            evidence = "Landing page reflects ongoing urgent or promotional context."
        else:
            status = "Urgency Missing"
            severity = "Medium"
            evidence = "Ad manufactures urgency ('hurry', 'limited time') but landing page has standard evergreen copy."

        rows.append({
            "Category": "Urgency & Scarcity",
            "Claim": claim,
            "Status": status,
            "Location": "Tone & Framing",
            "Severity": severity,
            "Evidence": evidence
        })

    return rows

def compute_claim_fidelity_score(claim_rows: List[Dict[str, Any]]) -> int:
    """Calculate 0-100 score based on verified claims and discrepancy weights."""
    if not claim_rows:
        return 100
    
    score_weights = {
        "Supported (Hero)": 1.0,
        "Supported (Body)": 0.95,
        "Supported (Date Match)": 1.0,
        "Urgency Reflected": 0.90,
        "Partial Match": 0.60,
        "Qualified / Hedged": 0.50,
        "Not explicitly supported": 0.40,
        "Urgency Missing": 0.45,
        "Buried in Fine Print": 0.25,
        "Not found on page": 0.0,
        "Date Mismatch": 0.0,
        "Expired": 0.0
    }
    
    total_pts = sum(score_weights.get(r["Status"], 0.3) for r in claim_rows)
    raw_score = (total_pts / len(claim_rows)) * 100
    return max(0, min(100, round(raw_score)))
