"""
Multi-Sheet Excel Report Exporter using openpyxl.
Includes Executive Summary, Detailed Claims, Compliance Risks, and Visual Scores.
"""

import io
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def generate_excel_report(audit_data: Dict[str, Any]) -> bytes:
    """Generate professional styled Excel workbook."""
    wb = openpyxl.Workbook()
    
    # Fonts & Styles
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=14, bold=True, color="1E293B")
    bold_font = Font(name="Calibri", size=10, bold=True)
    normal_font = Font(name="Calibri", size=10)
    
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    accent_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    pass_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    fail_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    warn_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )
    
    # ------------------ SHEET 1: Summary ------------------
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    ws_summary.views.sheetView[0].showGridLines = True
    
    ws_summary["A1"] = "MessageMatch Enterprise - Audit Summary"
    ws_summary["A1"].font = title_font
    
    summary_rows = [
        ("Brand / Advertiser", audit_data.get("brand", "N/A")),
        ("Landing Page URL", audit_data.get("url", "N/A")),
        ("Audit Date", audit_data.get("checked_time", "N/A")),
        ("Overall Match Score", f"{audit_data.get('score', 0)} / 100"),
        ("Predicted Google Quality Score", f"{audit_data.get('quality_score', {}).get('quality_score', 'N/A')} / 10"),
        ("Estimated CPC Impact", f"{audit_data.get('quality_score', {}).get('cpc_impact_pct', 0.0):+}%"),
        ("Total Claims Analyzed", len(audit_data.get("rows", []))),
        ("Issues / Mismatches Flagged", sum(not r.get("Status", "").startswith("Supported") for r in audit_data.get("rows", []))),
        ("Regulatory Infractions Detected", len(audit_data.get("compliance_findings", [])))
    ]
    
    ws_summary["A3"] = "Metric"
    ws_summary["B3"] = "Value"
    ws_summary["A3"].font = header_font
    ws_summary["B3"].font = header_font
    ws_summary["A3"].fill = header_fill
    ws_summary["B3"].fill = header_fill
    
    for idx, (label, val) in enumerate(summary_rows, start=4):
        ws_summary[f"A{idx}"] = label
        ws_summary[f"B{idx}"] = val
        ws_summary[f"A{idx}"].font = bold_font
        ws_summary[f"B{idx}"].font = normal_font
        ws_summary[f"A{idx}"].border = thin_border
        ws_summary[f"B{idx}"].border = thin_border
        if idx % 2 == 0:
            ws_summary[f"A{idx}"].fill = accent_fill
            ws_summary[f"B{idx}"].fill = accent_fill
            
    ws_summary.column_dimensions["A"].width = 30
    ws_summary.column_dimensions["B"].width = 50

    # ------------------ SHEET 2: Claims Breakdown ------------------
    ws_claims = wb.create_sheet(title="Claims Breakdown")
    ws_claims.views.sheetView[0].showGridLines = True
    
    headers = ["Category", "Ad Claim", "Status", "Page Location", "Severity", "Evidence"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws_claims.cell(row=1, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    for row_idx, claim in enumerate(audit_data.get("rows", []), 2):
        status = claim.get("Status", "")
        status_fill = pass_fill if status.startswith("Supported") else (fail_fill if status in ("Not found on page", "Expired", "Date Mismatch") else warn_fill)
        
        c1 = ws_claims.cell(row=row_idx, column=1, value=claim.get("Category", ""))
        c2 = ws_claims.cell(row=row_idx, column=2, value=claim.get("Claim", ""))
        c3 = ws_claims.cell(row=row_idx, column=3, value=status)
        c4 = ws_claims.cell(row=row_idx, column=4, value=claim.get("Location", ""))
        c5 = ws_claims.cell(row=row_idx, column=5, value=claim.get("Severity", ""))
        c6 = ws_claims.cell(row=row_idx, column=6, value=claim.get("Evidence", ""))
        
        c3.fill = status_fill
        for c in (c1, c2, c3, c4, c5, c6):
            c.font = normal_font
            c.border = thin_border

    ws_claims.column_dimensions["A"].width = 22
    ws_claims.column_dimensions["B"].width = 35
    ws_claims.column_dimensions["C"].width = 24
    ws_claims.column_dimensions["D"].width = 18
    ws_claims.column_dimensions["E"].width = 14
    ws_claims.column_dimensions["F"].width = 50

    # ------------------ SHEET 3: Regulatory Findings ------------------
    ws_reg = wb.create_sheet(title="Regulatory & Dark Patterns")
    ws_reg.views.sheetView[0].showGridLines = True
    
    reg_headers = ["Framework", "Issue Type", "Severity", "Trigger Phrase", "Finding", "Remediation"]
    for col_idx, h in enumerate(reg_headers, 1):
        cell = ws_reg.cell(row=1, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    for row_idx, f in enumerate(audit_data.get("compliance_findings", []), 2):
        ws_reg.cell(row=row_idx, column=1, value=f.get("framework", "")).border = thin_border
        ws_reg.cell(row=row_idx, column=2, value=f.get("type", "")).border = thin_border
        ws_reg.cell(row=row_idx, column=3, value=f.get("severity", "")).border = thin_border
        ws_reg.cell(row=row_idx, column=4, value=f.get("trigger", "")).border = thin_border
        ws_reg.cell(row=row_idx, column=5, value=f.get("finding", "")).border = thin_border
        ws_reg.cell(row=row_idx, column=6, value=f.get("recommendation", "")).border = thin_border

    ws_reg.column_dimensions["A"].width = 26
    ws_reg.column_dimensions["B"].width = 22
    ws_reg.column_dimensions["C"].width = 14
    ws_reg.column_dimensions["D"].width = 20
    ws_reg.column_dimensions["E"].width = 40
    ws_reg.column_dimensions["F"].width = 45

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
