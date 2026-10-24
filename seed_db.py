"""
Seed script to pre-populate SQLite database with realistic audit case studies.
"""

import database
from demo_data import DEMO_SCENARIOS
from core.claim_engine import analyze_claims, compute_claim_fidelity_score
from core.compliance_engine import audit_compliance_risks, compute_compliance_score
from core.quality_score import estimate_quality_score

def seed():
    for name, data in DEMO_SCENARIOS.items():
        brand = data["brand"]
        ad_copy = data["ad_copy"]
        url = data["url"]
        ad_fmt = data["ad_format"]
        landing_text = data["landing_text"]
        
        claims = analyze_claims(ad_copy, landing_text)
        fid_score = compute_claim_fidelity_score(claims)
        risks = audit_compliance_risks(ad_copy, landing_text)
        comp_score = compute_compliance_score(risks)
        
        qs = estimate_quality_score(fid_score, 75, comp_score)
        overall = round((fid_score * 0.5) + (comp_score * 0.3) + (qs["composite_pct"] * 0.2))
        
        report_data = {
            "uuid": "seed-" + brand.lower().replace(" ", "")[:4],
            "brand": brand,
            "ad_copy": ad_copy,
            "ad_format": ad_fmt,
            "url": url,
            "score": overall,
            "rows": claims,
            "compliance_findings": risks,
            "quality_score": qs,
            "checked_time": "2026-10-24 18:00:00"
        }
        
        database.save_audit(
            audit_uuid=report_data["uuid"],
            brand=brand,
            ad_copy=ad_copy,
            landing_url=url,
            ad_format=ad_fmt,
            overall_score=overall,
            quality_score=qs["quality_score"],
            visual_score=75.0,
            regulatory_score=comp_score,
            claims_count=len(claims),
            issues_count=sum(not c.get("Status","").startswith("Supported") for c in claims),
            status_label="High Match" if overall >= 80 else ("Moderate" if overall >= 50 else "High Risk"),
            ad_image_thumb=None,
            report_data=report_data
        )
    print("Database seeded successfully with 4 enterprise audits.")

if __name__ == "__main__":
    seed()
