"""
Custom HTML/CSS UI Components, Badges, and Styled Containers.
"""

import html

def render_hero_banner():
    return """
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 70%, #6366f1 100%);
                border-radius: 20px; padding: 28px 32px; color: #ffffff; margin-bottom: 24px;
                box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.35); position: relative; overflow: hidden;">
        <div style="position: relative; z-index: 2;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.15);
                        backdrop-filter: blur(8px); padding: 4px 14px; border-radius: 999px; font-size: 0.78rem;
                        font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px;">
                ⚡ Enterprise Edition v2.4
            </div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; letter-spacing: -0.02em; color: #ffffff;">
                MessageMatch Enterprise
            </h1>
            <p style="margin: 6px 0 0 0; opacity: 0.92; font-size: 1.02rem; font-weight: 400; max-width: 800px;">
                AI & Heuristic Ad-to-Landing-Page Match & Regulatory Compliance Audit Suite.
                Eliminate message mismatch, prevent FTC penalties, and reclaim up to 40% in wasted ad spend.
            </p>
        </div>
    </div>
    """

def render_claim_card(claim_data: dict) -> str:
    category = html.escape(claim_data.get("Category", "Claim"))
    claim = html.escape(claim_data.get("Claim", ""))
    status = html.escape(claim_data.get("Status", ""))
    location = html.escape(claim_data.get("Location", ""))
    severity = html.escape(claim_data.get("Severity", "Pass"))
    evidence = html.escape(claim_data.get("Evidence", ""))
    
    # Border & Badge styling based on status
    if status.startswith("Supported") or status == "Urgency Reflected":
        border_color = "#16a34a"
        bg_card = "rgba(22, 163, 74, 0.04)"
        badge_class = "background: rgba(22, 163, 74, 0.15); color: #15803d;"
    elif status in ("Not found on page", "Expired", "Date Mismatch"):
        border_color = "#dc2626"
        bg_card = "rgba(220, 38, 38, 0.04)"
        badge_class = "background: rgba(220, 38, 38, 0.15); color: #b91c1c;"
    else:
        border_color = "#d97706"
        bg_card = "rgba(217, 119, 6, 0.04)"
        badge_class = "background: rgba(217, 119, 6, 0.15); color: #b45309;"

    sev_bg = "#dc2626" if severity in ("Critical", "High") else ("#d97706" if severity == "Medium" else "#16a34a")

    return f"""
    <div style="border: 1px solid rgba(128,128,128,0.2); border-left: 5px solid {border_color};
                background: {bg_card}; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; gap: 6px; align-items: center;">
                <span style="background: rgba(99, 102, 241, 0.12); color: #4f46e5; font-size: 0.75rem;
                             font-weight: 700; padding: 3px 10px; border-radius: 999px;">
                    {category}
                </span>
                <span style="{badge_class} font-size: 0.75rem; font-weight: 700; padding: 3px 10px; border-radius: 999px;">
                    {status}
                </span>
                <span style="background: rgba(100, 116, 139, 0.12); color: #475569; font-size: 0.72rem;
                             padding: 2px 8px; border-radius: 6px;">
                    📍 {location}
                </span>
            </div>
            <span style="background: {sev_bg}; color: #ffffff; font-size: 0.7rem; font-weight: 700;
                         padding: 2px 8px; border-radius: 6px; text-transform: uppercase;">
                {severity}
            </span>
        </div>
        <div style="font-size: 1.05rem; font-weight: 700; margin: 9px 0 6px 0; color: #1e293b;">
            &ldquo;{claim}&rdquo;
        </div>
        <div style="font-size: 0.88rem; color: #475569; line-height: 1.45;">
            <strong>Verification Evidence:</strong> {evidence}
        </div>
    </div>
    """

def render_score_ring(score: int, label: str = "Match Fidelity") -> str:
    color = "#16a34a" if score >= 80 else ("#f59e0b" if score >= 50 else "#dc2626")
    return f"""
    <div style="text-align: center; padding: 12px 0;">
        <div style="width: 140px; height: 140px; border-radius: 50%; margin: 0 auto;
                    background: conic-gradient({color} {score * 3.6}deg, rgba(128,128,128,0.18) 0);
                    display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
            <div style="width: 106px; height: 106px; border-radius: 50%; background: #ffffff;
                        display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <b style="font-size: 2.2rem; font-weight: 800; color: #0f172a; line-height: 1;">{score}</b>
                <small style="font-size: 0.75rem; font-weight: 600; color: #64748b; margin-top: 2px;">/ 100</small>
            </div>
        </div>
        <div style="margin-top: 10px; font-weight: 700; font-size: 1.05rem; color: {color};">
            {label}
        </div>
    </div>
    """
