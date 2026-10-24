"""
Unit and integration test script for MessageMatch Enterprise.
"""

import sys
from demo_data import DEMO_SCENARIOS
from core.claim_engine import analyze_claims, compute_claim_fidelity_score
from core.compliance_engine import audit_compliance_risks, compute_compliance_score
from core.quality_score import estimate_quality_score
from core.remediation import generate_remediation_suggestions
from exporters.pdf_exporter import generate_pdf_report
from exporters.excel_exporter import generate_excel_report
from exporters.html_exporter import generate_html_report
import database

def run_tests():
    print("Testing core claim and regulatory engines...")
    scn = DEMO_SCENARIOS["FinTech Loan Approval (Speed & Fee Trap)"]
    claims = analyze_claims(scn["ad_copy"], scn["landing_text"])
    assert len(claims) > 0, "Claims extraction failed"
    print(f"Extracted {len(claims)} claims successfully.")

    fid_score = compute_claim_fidelity_score(claims)
    assert 0 <= fid_score <= 100, "Fidelity score out of bounds"
    print(f"Fidelity score: {fid_score}")

    risks = audit_compliance_risks(scn["ad_copy"], scn["landing_text"])
    comp_score = compute_compliance_score(risks)
    print(f"Compliance risks detected: {len(risks)}, score: {comp_score}")

    qs = estimate_quality_score(fid_score, 75, comp_score)
    assert 1 <= qs["quality_score"] <= 10, "Quality score out of range"
    print(f"Predicted Quality score: {qs['quality_score']}/10, CPC impact: {qs['cpc_impact_pct']}%")

    remed = generate_remediation_suggestions(scn["ad_copy"], scn["brand"], claims, risks)
    assert len(remed["ad_variants"]) > 0, "Remediation generation failed"
    print(f"Generated {len(remed['ad_variants'])} copy variants.")

    # Test Exporters
    audit_payload = {
        "brand": scn["brand"],
        "url": scn["url"],
        "ad_copy": scn["ad_copy"],
        "score": 75,
        "rows": claims,
        "compliance_findings": risks,
        "quality_score": qs,
        "checked_time": "2026-10-24 18:00:00"
    }

    print("Testing PDF exporter...")
    pdf_bytes = generate_pdf_report(audit_payload)
    assert len(pdf_bytes) > 500, "PDF export produced empty or corrupted output"
    print(f"PDF generated ({len(pdf_bytes)} bytes)")

    print("Testing Excel exporter...")
    xlsx_bytes = generate_excel_report(audit_payload)
    assert len(xlsx_bytes) > 500, "Excel export produced empty output"
    print(f"Excel workbook generated ({len(xlsx_bytes)} bytes)")

    print("Testing HTML exporter...")
    html_out = generate_html_report(audit_payload)
    assert "<html" in html_out and scn["brand"] in html_out, "HTML export missing key tags"
    print(f"HTML report generated ({len(html_out)} chars)")

    print("Testing SQLite persistence...")
    stats = database.get_stats()
    assert stats["total_audits"] > 0, "No audits found in DB"
    print(f"Database stats verified: {stats}")

    print("\nALL INTEGRATION TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    run_tests()
