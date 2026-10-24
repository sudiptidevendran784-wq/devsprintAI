"""
Plotly Visualizations and Diagnostic Charts for MessageMatch Enterprise.
"""

from typing import Dict, Any, List
import plotly.graph_objects as go

def create_radar_chart(audit_data: Dict[str, Any]) -> go.Figure:
    """Radar chart comparing multi-dimensional audit scores."""
    claim_score = audit_data.get("score", 70)
    visual_score = audit_data.get("visual_score", 75)
    compliance_score = audit_data.get("compliance_score", 85)
    qs_pct = audit_data.get("quality_score", {}).get("composite_pct", 75)
    
    categories = [
        "Claim Fidelity",
        "Visual Consistency",
        "Regulatory Safety",
        "Hero Placement",
        "Ad Relevance"
    ]
    
    values = [
        claim_score,
        visual_score,
        compliance_score,
        min(100, int(claim_score * 1.1)) if audit_data.get("has_hero_match", True) else int(claim_score * 0.7),
        min(100, int(qs_pct))
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.25)',
        line=dict(color='#4f46e5', width=2.5),
        name='Current Audit'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[85, 80, 95, 85, 90, 85],
        theta=categories + [categories[0]],
        line=dict(color='#10b981', width=1.5, dash='dot'),
        name='Top Tier Benchmark'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=35, r=35, t=25, b=25),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_claims_donut(claims: List[Dict[str, Any]]) -> go.Figure:
    """Donut chart showing verified vs flagged claims."""
    supported = sum(1 for c in claims if c.get("Status", "").startswith("Supported"))
    needs_review = sum(1 for c in claims if c.get("Status", "") in ("Qualified / Hedged", "Partial Match", "Urgency Missing", "Buried in Fine Print"))
    critical = sum(1 for c in claims if c.get("Status", "") in ("Not found on page", "Expired", "Date Mismatch"))
    
    labels = ["Supported", "Needs Review", "Missing / Flagged"]
    values = [supported, needs_review, critical]
    colors = ["#16a34a", "#f59e0b", "#dc2626"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors),
        textinfo="value+percent",
        hoverinfo="label+value"
    )])
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=10, b=25),
        height=240,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig
