"""
Standalone Interactive HTML Report Generator for MessageMatch Enterprise.
"""

import html
from typing import Dict, Any

def generate_html_report(audit_data: Dict[str, Any]) -> str:
    brand = html.escape(audit_data.get("brand", "General Brand"))
    url = html.escape(audit_data.get("url", "N/A"))
    score = audit_data.get("score", 0)
    qs = audit_data.get("quality_score", {}).get("quality_score", "N/A")
    cpc = audit_data.get("quality_score", {}).get("cpc_impact_pct", 0.0)
    claims = audit_data.get("rows", [])
    findings = audit_data.get("compliance_findings", [])
    ad_copy = html.escape(audit_data.get("ad_copy", ""))
    
    score_color = "#16a34a" if score >= 80 else ("#f59e0b" if score >= 50 else "#dc2626")
    
    claims_rows_html = ""
    for c in claims:
        st = c.get("Status", "")
        badge_cls = "badge-pass" if st.startswith("Supported") else ("badge-fail" if st in ("Not found on page", "Expired", "Date Mismatch") else "badge-warn")
        claims_rows_html += f"""
        <tr>
            <td><span class="badge badge-cat">{html.escape(c.get('Category', ''))}</span></td>
            <td><strong>{html.escape(c.get('Claim', ''))}</strong></td>
            <td><span class="badge {badge_cls}">{html.escape(st)}</span></td>
            <td>{html.escape(c.get('Location', ''))}</td>
            <td><span class="severity-{c.get('Severity', '').lower()}">{html.escape(c.get('Severity', ''))}</span></td>
            <td class="text-evidence">{html.escape(c.get('Evidence', ''))}</td>
        </tr>
        """
        
    findings_html = ""
    for f in findings:
        findings_html += f"""
        <div class="card finding-card">
            <div class="finding-header">
                <span class="badge badge-fail">{html.escape(f.get('severity', 'High'))}</span>
                <strong>{html.escape(f.get('type', ''))}</strong> &mdash; <em>{html.escape(f.get('framework', ''))}</em>
            </div>
            <p><strong>Trigger:</strong> {html.escape(f.get('trigger', ''))}</p>
            <p>{html.escape(f.get('finding', ''))}</p>
            <div class="remediation"><strong>Remediation:</strong> {html.escape(f.get('recommendation', ''))}</div>
        </div>
        """
    if not findings:
        findings_html = "<p class='text-muted'>No major regulatory or deceptive dark patterns detected.</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Report | {brand} | MessageMatch Enterprise</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: #ffffff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); padding: 32px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; }}
        .logo {{ font-size: 22px; font-weight: 800; color: #4f46e5; }}
        .score-circle {{ width: 90px; height: 90px; border-radius: 50%; border: 6px solid {score_color}; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 800; font-size: 28px; color: {score_color}; }}
        .score-circle small {{ font-size: 11px; font-weight: 500; color: #64748b; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 24px 0; }}
        .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; }}
        .metric-val {{ font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 4px; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
        .badge-cat {{ background: #e0e7ff; color: #4338ca; }}
        .badge-pass {{ background: #dcfce7; color: #15803d; }}
        .badge-warn {{ background: #fef3c7; color: #b45309; }}
        .badge-fail {{ background: #fee2e2; color: #b91c1c; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; font-weight: 600; }}
        .finding-card {{ border-left: 4px solid #dc2626; background: #fff5f5; padding: 14px; border-radius: 8px; margin-bottom: 12px; font-size: 13px; }}
        .remediation {{ background: #eff6ff; border-left: 3px solid #3b82f6; padding: 8px 12px; border-radius: 6px; margin-top: 6px; color: #1e40af; }}
        .quote-box {{ background: #f8fafc; border-left: 4px solid #6366f1; padding: 12px 16px; border-radius: 6px; font-style: italic; margin: 16px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="logo">🎯 MessageMatch Enterprise</div>
                <div style="color: #64748b; font-size: 13px; margin-top: 4px;">Ad-to-Landing-Page Match & Regulatory Compliance Audit</div>
                <div style="font-weight: 600; font-size: 16px; margin-top: 8px;">Brand: {brand}</div>
                <div style="font-size: 12px; color: #64748b;">Target URL: {url}</div>
            </div>
            <div class="score-circle">
                {score}
                <small>SCORE</small>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <small style="color: #64748b;">Predicted Quality Score</small>
                <div class="metric-val">{qs} / 10</div>
            </div>
            <div class="metric-card">
                <small style="color: #64748b;">Estimated CPC Impact</small>
                <div class="metric-val" style="color: {'#16a34a' if cpc <= 0 else '#dc2626'}">{cpc:+}%</div>
            </div>
            <div class="metric-card">
                <small style="color: #64748b;">Claims Analyzed</small>
                <div class="metric-val">{len(claims)}</div>
            </div>
            <div class="metric-card">
                <small style="color: #64748b;">Issues / Flags</small>
                <div class="metric-val">{sum(not c.get('Status', '').startswith('Supported') for c in claims)}</div>
            </div>
        </div>

        <h3>Ad Copy Evaluated</h3>
        <div class="quote-box">&ldquo;{ad_copy}&rdquo;</div>

        <h3>Claim Verification Breakdown</h3>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Ad Claim</th>
                    <th>Status</th>
                    <th>Zone</th>
                    <th>Severity</th>
                    <th>Evidence</th>
                </tr>
            </thead>
            <tbody>
                {claims_rows_html}
            </tbody>
        </table>

        <h3 style="margin-top: 32px;">Regulatory & Dark Pattern Findings</h3>
        {findings_html}

        <div style="margin-top: 40px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 16px;">
            Generated by MessageMatch Enterprise &bull; Confidential &bull; Rule-based screening with heuristic verification
        </div>
    </div>
</body>
</html>
"""
    return html_content
