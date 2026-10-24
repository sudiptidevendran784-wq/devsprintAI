"""
Professional PDF Audit Report Generator using fpdf2.
"""

import io
from datetime import datetime
from typing import Dict, Any
from fpdf import FPDF

class AuditPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(79, 70, 229)
        self.cell(0, 10, "MessageMatch Enterprise | Compliance & Match Audit", ln=True, align="L")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}", ln=True, align="L")
        self.line(10, 26, 200, 26)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - Confidential Audit Report - MessageMatch Enterprise", align="C")

def generate_pdf_report(audit_data: Dict[str, Any]) -> bytes:
    """Generate high-density PDF report binary for download."""
    pdf = AuditPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()
    
    brand = audit_data.get("brand", "General Brand")
    url = audit_data.get("url", "N/A")
    score = audit_data.get("score", 0)
    qs = audit_data.get("quality_score", {}).get("quality_score", "N/A")
    ad_copy = audit_data.get("ad_copy", "")
    claims = audit_data.get("rows", [])
    findings = audit_data.get("compliance_findings", [])
    
    # 1. Executive Summary Box
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(10, 30, 190, 38, style="F")
    
    pdf.set_xy(14, 33)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(100, 6, f"Brand: {brand}", ln=False)
    
    # Overall Score Pill
    pdf.set_xy(140, 33)
    pdf.set_font("Helvetica", "B", 13)
    if score >= 80:
        pdf.set_text_color(22, 163, 74)
    elif score >= 50:
        pdf.set_text_color(217, 119, 6)
    else:
        pdf.set_text_color(220, 38, 38)
    pdf.cell(55, 6, f"Score: {score}/100", ln=True, align="R")
    
    pdf.set_xy(14, 40)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 5, f"Landing Page: {url[:80]}", ln=True)
    
    pdf.set_xy(14, 46)
    pdf.cell(0, 5, f"Predicted Google Quality Score: {qs}/10  |  Total Claims Analyzed: {len(claims)}", ln=True)
    
    pdf.set_xy(14, 52)
    issues_count = sum(not c.get("Status", "").startswith("Supported") for c in claims)
    pdf.cell(0, 5, f"Discrepancies / Flags: {issues_count}  |  Compliance Infractions: {len(findings)}", ln=True)
    
    pdf.ln(18)
    
    # 2. Ad Copy Tested
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "Advertisement Copy Audited:", ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(190, 5, f'"{ad_copy}"')
    pdf.ln(4)
    
    # 3. Claims Verification Table
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "Claim Verification Breakdown:", ln=True)
    
    # Table Header
    pdf.set_fill_color(230, 235, 245)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(35, 6, "Category", border=1, fill=True)
    pdf.cell(45, 6, "Ad Claim", border=1, fill=True)
    pdf.cell(32, 6, "Match Status", border=1, fill=True)
    pdf.cell(78, 6, "Evidence / Discrepancy", border=1, fill=True, ln=True)
    
    pdf.set_font("Helvetica", "", 7.5)
    for c in claims[:12]:
        cat = c.get("Category", "")[:20]
        claim = c.get("Claim", "")[:26]
        status = c.get("Status", "")[:18]
        ev = c.get("Evidence", "")[:50]
        
        pdf.cell(35, 5.5, cat, border=1)
        pdf.cell(45, 5.5, claim, border=1)
        
        if status.startswith("Supported"):
            pdf.set_text_color(22, 163, 74)
        elif status in ("Not found on page", "Expired", "Date Mismatch"):
            pdf.set_text_color(220, 38, 38)
        else:
            pdf.set_text_color(217, 119, 6)
            
        pdf.cell(32, 5.5, status, border=1)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(78, 5.5, ev, border=1, ln=True)
        
    pdf.ln(5)
    
    # 4. Compliance & Dark Pattern Findings
    if findings:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 6, "Regulatory & Dark Pattern Findings:", ln=True)
        
        for f in findings[:4]:
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(220, 38, 38)
            pdf.cell(0, 5, f"[{f.get('severity', 'High')}] {f.get('type', 'Issue')} ({f.get('framework', '')})", ln=True)
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(190, 4, f"Finding: {f.get('finding', '')}")
            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(79, 70, 229)
            pdf.multi_cell(190, 4, f"Action: {f.get('recommendation', '')}")
            pdf.ln(2)

    return bytes(pdf.output())
