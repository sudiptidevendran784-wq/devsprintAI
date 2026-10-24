"""
Configuration and Rule Definitions for MessageMatch Enterprise.
"""

APP_NAME = "MessageMatch Enterprise"
APP_SUBTITLE = "AI-Powered Ad-to-Landing-Page Match & Regulatory Compliance Audit Suite"
APP_VERSION = "2.4.0"

# User-Agent for polite scraping
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 MessageMatch/2.4"

# Default skip domains for search discovery
SKIP_DOMAINS = (
    "facebook.com", "youtube.com", "reddit.com", "quora.com", "wikipedia.org",
    "pinterest.com", "linkedin.com", "twitter.com", "x.com", "instagram.com",
    "tiktok.com", "amazon.com/gp", "ebay.com"
)

# Hedge words indicating ambiguous or conditional landing page text
HEDGES = [
    "vary", "varies", "depend", "depends", "subject to", "eligib", "terms apply",
    "conditions apply", "may ", "might", "up to", "verification", "qualified buyers",
    "see store", "limited availability", "restrictions apply", "select models",
    "as low as", "starting at", "participating locations", "credit approval"
]

# Standard Claim Rules with Regex Patterns and Categorization
CLAIM_RULES = {
    "Speed & Turnaround": {
        "pattern": r"\b(?:in|within)\s+(?:one|1|\d+)\s+(?:day|hour|minute)s?|same[- ]day|24[- ]?hours?|instant(?:ly)?|overnight|real[- ]time|in minutes\b",
        "description": "Promises regarding speed of service, delivery, or processing",
        "severity": "High"
    },
    "Pricing & Discounts": {
        "pattern": r"\b\d+\s?%\s?off\b|\bsave\s+(?:\$|₹|€|£)?\s?\d+[%kK]?\b|[$₹€£]\s?\d+(?:[\d,.]*\d)?|\b\d+\s?(?:usd|inr|eur|gbp)\b|half[- ]price|bogo|buy 1 get 1",
        "description": "Explicit prices, percentage discounts, or savings figures",
        "severity": "Critical"
    },
    "Fees & Transparency": {
        "pattern": r"\bno (?:hidden )?fees?\b|\bzero (?:fees|processing fees?|commission)\b|\bfee[- ]free\b|\bno charges?\b|\bno interest for\b|\btransparent pricing\b",
        "description": "Zero fees or fee waiver promises",
        "severity": "Critical"
    },
    "Free Trials & Gifts": {
        "pattern": r"\bfree\b(?:\s+(?:trial|shipping|consultation|gift|quote|demo|sample|forever|delivery|tier|upgrade|tier))?\b",
        "description": "Free offers, no-cost services, gifts or trials",
        "severity": "High"
    },
    "Guarantees & Safety": {
        "pattern": r"\bguarantee[d]?\b|\bmoney[- ]back\b|\brisk[- ]free\b|100%\s+(?:safe|secure|satisfaction)|\bno[- ]questions[- ]asked\b|\bcancel anytime\b",
        "description": "Warranties, guarantees, security badges and return policies",
        "severity": "High"
    },
    "Rates & Financing": {
        "pattern": r"\b\d+(?:\.\d+)?\s?%\s?(?:apr|interest|rate|p\.a\.)\b|\blowest (?:rate|price|apr)\b|\bbest (?:rate|price)\b|\blowest price guarantee\b",
        "description": "Interest rates, APRs, and superlative financing claims",
        "severity": "Critical"
    },
    "Exclusivity & Accreditations": {
        "pattern": r"\b#1\b|\brated #?1\b|\bofficial\b|\bcertified\b|\baward[- ]winning\b|\bdoctor[- ]recommended\b|\bfda[- ]approved\b|\bpatent(?:ed)?\b",
        "description": "Rankings, awards, endorsements or regulatory certifications",
        "severity": "Critical"
    }
}

# Dark Pattern & Regulatory Heuristics
REGULATORY_PATTERNS = {
    "Deceptive Urgency": r"\bonly\s+\d+\s+left\b|\bhurry\b|\blast chance\b|\bdemand is high\b|\bclaim yours now\b",
    "Hidden Auto-Renewal": r"\bauto[- ]renew(?:al|s|ing)?\b|\bbilled annually after\b|\bsubscription renews\b|\brenews at normal rate\b",
    "Conditional Asterisks": r"\*|\bterms & conditions apply\b|\bsee details below\b|\bsubject to change without notice\b",
    "Unsubstantiated Health Claim": r"\bcure[s]?\b|\bprevents? disease\b|\bguaranteed weight loss\b|\bmiracle\b|\banti[- ]aging breakthrough\b"
}

# Quality Score Simulation Weights
QUALITY_SCORE_WEIGHTS = {
    "claim_fidelity": 0.45,
    "urgency_deadline": 0.20,
    "visual_coherence": 0.20,
    "regulatory_compliance": 0.15
}
