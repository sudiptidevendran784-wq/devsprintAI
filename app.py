"""
MessageMatch Enterprise - Full Advanced Application
AI-Powered Ad-to-Landing-Page Match & Regulatory Compliance Audit Suite
"""

import io
import os
import re
import html
import json
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import streamlit as st
from PIL import Image

import config
import database
from core.scraper import fetch_landing_page
from core.claim_engine import analyze_claims, compute_claim_fidelity_score
from core.visual_engine import (
    download_image, image_to_base64_thumb, visual_similarity,
    extract_dominant_colors, calculate_color_harmony_score, extract_ocr_text
)
from core.compliance_engine import audit_compliance_risks, compute_compliance_score
from core.quality_score import estimate_quality_score
from core.remediation import generate_remediation_suggestions
from core.search import search_landing_pages
from exporters.pdf_exporter import generate_pdf_report
from exporters.excel_exporter import generate_excel_report
from exporters.html_exporter import generate_html_report
from components.ui_cards import render_hero_banner, render_claim_card, render_score_ring
from components.charts import create_radar_chart, create_claims_donut
from components.diff_viewer import render_ad_mockup, render_color_palette_comparison
from demo_data import DEMO_SCENARIOS

# Page configuration
st.set_page_config(
    page_title=f"{config.APP_NAME}",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
CUSTOM_CSS = """
<style>
.block-container { padding-top: 1.5rem; max-width: 1300px; }
.metric-box {
    background: rgba(128,128,128,0.06);
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
}
.metric-label { font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; }
.metric-value { font-size: 1.6rem; font-weight: 800; color: #0f172a; margin-top: 2px; }
.step-header { display: flex; align-items: center; gap: 10px; margin: 20px 0 10px; }
.step-num {
    background: #4f46e5; color: #ffffff; border-radius: 50%;
    width: 28px; height: 28px; display: inline-flex; align-items: center;
    justify-content: center; font-weight: 700; font-size: 0.88rem;
}
.step-title { font-size: 1.18rem; font-weight: 700; color: #1e293b; }
.stTabs [data-baseweb="tab-list"] { gap: 12px; }
.stTabs [data-baseweb="tab"] {
    padding: 8px 18px; border-radius: 8px; font-weight: 600;
}
.remed-card {
    border: 1px solid #cbd5e1; border-radius: 10px; padding: 14px 16px;
    background: #f8fafc; margin-bottom: 12px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------- SIDEBAR NAVIGATION -----------------
with st.sidebar:
    st.markdown("### 🎯 **MessageMatch**")
    st.caption("Enterprise Ad & Landing Page Auditor")
    
    nav_mode = st.radio(
        "Navigation",
        [
            "Audit Studio (Single Ad)",
            "Batch Auditor (Bulk CSV)",
            "Campaigns & History",
            "Benchmark Comparison",
            "Rule & Compliance Engine",
            "Interactive Sandbox"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("#### 📊 **Global Audit Metrics**")
    db_stats = database.get_stats()
    c1, c2 = st.columns(2)
    c1.metric("Audits Run", db_stats["total_audits"])
    c2.metric("Avg Score", f"{db_stats['avg_overall_score']}%")
    c3, c4 = st.columns(2)
    c3.metric("Avg Quality", f"{db_stats['avg_quality_score']}/10")
    c4.metric("Flags Raised", db_stats["total_issues_flagged"])
    
    st.markdown("---")
    st.caption("MessageMatch Enterprise v2.4\nFTC 16 CFR Part 255 & ASCI Compliant Screening")


# ==============================================================================
# VIEW 1: AUDIT STUDIO (SINGLE AD CHECK)
# ==============================================================================
if nav_mode == "Audit Studio (Single Ad)":
    st.markdown(render_hero_banner(), unsafe_allow_html=True)
    
    # Preset quick loader
    with st.expander("⚡ Load Pre-Configured Enterprise Demo Scenarios (1-Click)", expanded=False):
        pcol1, pcol2 = st.columns([3, 1])
        with pcol1:
            selected_preset = st.selectbox("Choose Scenario:", list(DEMO_SCENARIOS.keys()))
        with pcol2:
            if st.button("Apply Scenario", use_container_width=True, type="secondary"):
                scn = DEMO_SCENARIOS[selected_preset]
                st.session_state["ad_text"] = scn["ad_copy"]
                st.session_state["brand_input"] = scn["brand"]
                st.session_state["ad_format"] = scn["ad_format"]
                st.session_state["landing_url"] = scn["url"]
                st.session_state["manual_text"] = scn["landing_text"].strip()
                st.rerun()

    # Step 1: The Advertisement
    st.markdown("<div class='step-header'><span class='step-num'>1</span><span class='step-title'>Advertisement Creative & Copy</span></div>", unsafe_allow_html=True)
    col_ad_copy, col_ad_creative = st.columns([3, 2], gap="large")
    
    with col_ad_copy:
        brand_val = st.text_input("Brand or Product Name", key="brand_input", value=st.session_state.get("brand_input", "Apex Lending Solutions"))
        c_fmt1, c_fmt2 = st.columns(2)
        with c_fmt1:
            ad_format = st.selectbox("Ad Format", ["Google Search", "Meta / Instagram", "Display Banner"], key="ad_format")
        with c_fmt2:
            target_audience = st.selectbox("Campaign Objective", ["Conversions / Leads", "Direct Sales", "Brand Consideration"])
            
        ad_copy_val = st.text_area(
            "Ad Copy / Headlines & Descriptions",
            key="ad_text",
            height=140,
            value=st.session_state.get("ad_text", "Get your personal loan approved in one day. 100% risk-free with zero fees and no hidden charges! 4.9% APR guaranteed. Offer ends Dec 31, 2026.")
        )
        
    with col_ad_creative:
        st.markdown("<small style='font-weight:700; color:#475569;'>AD CREATIVE / IMAGE</small>", unsafe_allow_html=True)
        up_file = st.file_uploader("Upload creative asset", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
        
        ad_image_obj = None
        if up_file:
            try:
                ad_image_obj = Image.open(up_file).convert("RGB")
                st.image(ad_image_obj, use_container_width=True)
                
                # OCR extraction action
                if st.button("📝 Extract Ad Copy via OCR", use_container_width=True):
                    ocr_res = extract_ocr_text(ad_image_obj)
                    if ocr_res["success"] and ocr_res["text"]:
                        st.session_state["ad_text"] = ocr_res["text"]
                        st.success("Extracted text from ad image successfully!")
                        st.rerun()
                    else:
                        st.warning(f"OCR Note: {ocr_res['message']}")
            except Exception as e:
                st.error(f"Error loading image: {e}")
        else:
            st.caption("Upload PNG/JPG creative to enable visual similarity, dominant color palette extraction, and hero image coherence checks.")

    # Step 2: Landing Page Discovery
    st.markdown("<div class='step-header'><span class='step-num'>2</span><span class='step-title'>Target Landing Page</span></div>", unsafe_allow_html=True)
    c_search_btn, c_url_input = st.columns([1.2, 2.8], gap="large")
    
    with c_search_btn:
        if st.button("🔎 Auto-Discover Landing Page", use_container_width=True):
            with st.spinner("Querying official domains..."):
                st.session_state["search_cands"] = search_landing_pages(ad_copy_val, brand_val)
                st.session_state.pop("picked_url", None)
                
    with c_url_input:
        target_url = st.text_input(
            "Or enter exact landing page URL:",
            key="landing_url",
            value=st.session_state.get("landing_url", "https://www.apexlending.com/instant-personal-loans"),
            placeholder="https://brand.com/offer"
        )

    # Search candidates cards
    cands = st.session_state.get("search_cands", [])
    if cands:
        st.markdown("<small style='font-weight:600; color:#64748b;'>SEARCH DISCOVERY RESULTS (Confirm advertiser domain):</small>", unsafe_allow_html=True)
        for i, cand in enumerate(cands[:4]):
            picked = (st.session_state.get("picked_url") == cand["url"])
            with st.container(border=True):
                col_c1, col_c2 = st.columns([4.2, 1], vertical_alignment="center")
                with col_c1:
                    st.markdown(f"**{cand['title']}**")
                    st.caption(f"`{cand['url']}` &bull; Domain match score: {cand['score']}")
                    st.write(cand["snippet"])
                with col_c2:
                    if st.button("✔ Pick" if picked else "Select URL", key=f"cand_pick_{i}", use_container_width=True, type="primary" if picked else "secondary"):
                        st.session_state["picked_url"] = cand["url"]
                        st.session_state["landing_url"] = cand["url"]
                        st.rerun()

    active_url = target_url.strip() or st.session_state.get("picked_url", "")
    
    with st.expander("📝 Manual Landing Page Text / Firewalled Page Bypass", expanded=bool(st.session_state.get("manual_text"))):
        manual_page_content = st.text_area(
            "Paste landing page text or HTML content directly:",
            key="manual_text",
            height=120,
            value=st.session_state.get("manual_text", "")
        )

    # Step 3: Run Audit
    st.markdown("<div class='step-header'><span class='step-num'>3</span><span class='step-title'>Execute Message Match Audit</span></div>", unsafe_allow_html=True)
    
    if st.button("🚀 Run Comprehensive Audit", type="primary", use_container_width=True):
        progress_bar = st.progress(10, text="Initializing audit engine...")
        
        # Scrape or use manual text
        page_data = {
            "success": True,
            "text": manual_page_content.strip(),
            "sections": {"above_the_fold": manual_page_content[:600], "footer_disclaimers": manual_page_content[-600:], "full_body": manual_page_content},
            "images": [],
            "load_time_ms": 320
        }
        
        if active_url and not manual_page_content.strip():
            progress_bar.progress(30, text=f"Fetching landing page from {active_url}...")
            page_data = fetch_landing_page(active_url)
            if not page_data["success"]:
                st.error(f"Failed to fetch {active_url}: {page_data['error']}. Using manual text or fallback.")
        
        final_page_text = page_data["text"] or manual_page_content.strip()
        
        if not final_page_text:
            st.warning("Please provide a valid landing page URL or paste the page text to proceed.")
        else:
            progress_bar.progress(55, text="Analyzing claim fidelity, deadlines and location zones...")
            claim_rows = analyze_claims(ad_copy_val, final_page_text, page_data.get("sections"))
            fidelity_score = compute_claim_fidelity_score(claim_rows)
            
            progress_bar.progress(70, text="Evaluating visual consistency, palettes, and hero elements...")
            # Visual analysis
            page_pics = []
            page_palette = []
            ad_palette = []
            visual_sim_score = 75
            color_harmony = 80
            
            if ad_image_obj:
                ad_palette = extract_dominant_colors(ad_image_obj)
            
            if page_data.get("images"):
                with ThreadPoolExecutor(max_workers=5) as ex:
                    dl_imgs = list(ex.map(download_image, page_data["images"][:5]))
                page_pics = [(u, im) for u, im in zip(page_data["images"][:5], dl_imgs) if im is not None]
                if page_pics:
                    page_palette = extract_dominant_colors(page_pics[0][1])
            
            if ad_image_obj and page_pics:
                visual_sim_score = max(visual_similarity(ad_image_obj, im) for _, im in page_pics)
                color_harmony = calculate_color_harmony_score(ad_palette, page_palette)
                
            progress_bar.progress(85, text="Running regulatory FTC & Dark Pattern screening...")
            footer_text = page_data.get("sections", {}).get("footer_disclaimers", "")
            compliance_findings = audit_compliance_risks(ad_copy_val, final_page_text, footer_text)
            comp_score = compute_compliance_score(compliance_findings)
            
            # Google Ads Quality Score & Auction Impact
            has_hero = any(r.get("Location") == "Above the Fold" and r.get("Status", "").startswith("Supported") for r in claim_rows)
            quality_metrics = estimate_quality_score(
                claim_score=fidelity_score,
                visual_score=color_harmony,
                compliance_score=comp_score,
                load_time_ms=page_data.get("load_time_ms", 400),
                has_above_fold_hero_match=has_hero
            )
            
            # AI Copy Remediation
            unverified = [r for r in claim_rows if not r.get("Status", "").startswith("Supported")]
            remediation = generate_remediation_suggestions(
                ad_copy=ad_copy_val,
                brand=brand_val,
                unverified_claims=unverified,
                regulatory_risks=compliance_findings,
                page_title=page_data.get("title", "")
            )
            
            overall_audit_score = round(
                (fidelity_score * config.QUALITY_SCORE_WEIGHTS["claim_fidelity"]) +
                (visual_sim_score * config.QUALITY_SCORE_WEIGHTS["visual_coherence"]) +
                (comp_score * config.QUALITY_SCORE_WEIGHTS["regulatory_compliance"]) +
                (quality_metrics["composite_pct"] * config.QUALITY_SCORE_WEIGHTS["urgency_deadline"])
            )
            overall_audit_score = max(0, min(100, overall_audit_score))
            
            audit_uuid = str(uuid.uuid4())[:8]
            audit_result = {
                "uuid": audit_uuid,
                "brand": brand_val,
                "ad_copy": ad_copy_val,
                "ad_format": ad_format,
                "url": active_url or "(Manual text)",
                "score": overall_audit_score,
                "fidelity_score": fidelity_score,
                "visual_score": visual_sim_score,
                "compliance_score": comp_score,
                "quality_score": quality_metrics,
                "rows": claim_rows,
                "compliance_findings": compliance_findings,
                "remediation": remediation,
                "has_hero_match": has_hero,
                "ad_image": ad_image_obj,
                "page_pics": page_pics,
                "ad_palette": ad_palette,
                "page_palette": page_palette,
                "color_harmony": color_harmony,
                "checked_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to SQLite database
            thumb = image_to_base64_thumb(ad_image_obj) if ad_image_obj else None
            issues_cnt = sum(not r.get("Status", "").startswith("Supported") for r in claim_rows)
            status_lbl = "High Match" if overall_audit_score >= 80 else ("Moderate" if overall_audit_score >= 50 else "High Risk")
            
            # Prepare serializable dict for database
            clean_save_dict = {k: v for k, v in audit_result.items() if k not in ("ad_image", "page_pics")}
            database.save_audit(
                audit_uuid=audit_uuid,
                brand=brand_val,
                ad_copy=ad_copy_val,
                landing_url=active_url,
                ad_format=ad_format,
                overall_score=overall_audit_score,
                quality_score=quality_metrics["quality_score"],
                visual_score=visual_sim_score,
                regulatory_score=comp_score,
                claims_count=len(claim_rows),
                issues_count=issues_cnt,
                status_label=status_lbl,
                ad_image_thumb=thumb,
                report_data=clean_save_dict
            )
            
            st.session_state["current_audit"] = audit_result
            progress_bar.progress(100, text="Audit completed successfully!")
            st.rerun()

    # ----------------- DISPLAY AUDIT RESULTS -----------------
    res = st.session_state.get("current_audit")
    if res:
        st.markdown("---")
        st.markdown(f"### 📋 **Audit Results: {res['brand']}**")
        st.caption(f"Audit UUID: `{res['uuid']}` &bull; Executed at: {res['checked_time']}")
        
        # 1. Executive Top Bar
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns([1.5, 1.2, 1.2, 1.2, 1.2])
        
        with m_col1:
            st.markdown(render_score_ring(res["score"], "Overall Match Fidelity"), unsafe_allow_html=True)
            
        with m_col2:
            qs_val = res["quality_score"]["quality_score"]
            cpc_val = res["quality_score"]["cpc_impact_pct"]
            cpc_sign = f"{cpc_val:+}%"
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-label'>Quality Score</div>
                <div class='metric-value' style='color:#4f46e5;'>{qs_val} <small style='font-size:1rem;'>/ 10</small></div>
                <small style='font-weight:600; color:{'#16a34a' if cpc_val <= 0 else '#dc2626'};'>Est. CPC Impact: {cpc_sign}</small>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            monthly_w = res["quality_score"]["monthly_waste_est"]
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-label'>Est. Ad Spend Surcharge</div>
                <div class='metric-value' style='color:{'#16a34a' if monthly_w == 0 else '#dc2626'};'>${monthly_w:,.0f}</div>
                <small style='color:#64748b;'>Based on $10k/mo budget</small>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col4:
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-label'>Claims Analyzed</div>
                <div class='metric-value'>{len(res['rows'])}</div>
                <small style='color:#dc2626; font-weight:600;'>{sum(not r.get('Status','').startswith('Supported') for r in res['rows'])} Discrepancies</small>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col5:
            reg_score = res["compliance_score"]
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-label'>Compliance Safety</div>
                <div class='metric-value' style='color:{'#16a34a' if reg_score >= 80 else '#dc2626'};'>{reg_score}%</div>
                <small style='color:#64748b;'>{len(res['compliance_findings'])} Flags</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Detailed Tabs
        tab_claims, tab_visual, tab_compliance, tab_remed, tab_preview, tab_charts, tab_exports = st.tabs([
            "🎯 Claim Verification Matrix",
            "🎨 Visual & Color Alignment",
            "⚖️ Regulatory & Dark Patterns",
            "💡 AI Copy Remediation",
            "📱 Live Ad & Page Mockup",
            "📊 Diagnostic Charts",
            "⬇️ Export Reports"
        ])
        
        # TAB 1: Claim Verification Matrix
        with tab_claims:
            st.markdown("#### **Verified Promises & Discrepancy Breakdown**")
            f_all, f_warn, f_pass = st.columns([1, 1, 1])
            subtab_all, subtab_warn, subtab_pass = st.tabs([
                f"All Claims ({len(res['rows'])})",
                f"Discrepancies & Flagged ({sum(not r.get('Status','').startswith('Supported') for r in res['rows'])})",
                f"Supported ({sum(r.get('Status','').startswith('Supported') for r in res['rows'])})"
            ])
            
            with subtab_all:
                for r in res["rows"]:
                    st.markdown(render_claim_card(r), unsafe_allow_html=True)
                    
            with subtab_warn:
                flagged = [r for r in res["rows"] if not r.get("Status","").startswith("Supported")]
                if not flagged:
                    st.success("🎉 Excellent! All claims made in the advertisement are explicitly confirmed on the landing page.")
                for r in flagged:
                    st.markdown(render_claim_card(r), unsafe_allow_html=True)
                    
            with subtab_pass:
                passed = [r for r in res["rows"] if r.get("Status","").startswith("Supported")]
                for r in passed:
                    st.markdown(render_claim_card(r), unsafe_allow_html=True)

        # TAB 2: Visual & Color Alignment
        with tab_visual:
            st.markdown("#### **Visual Continuity & Creative Coherence**")
            v_col1, v_col2 = st.columns(2, gap="large")
            with v_col1:
                st.markdown("**Ad Creative Asset**")
                if res["ad_image"]:
                    st.image(res["ad_image"], use_container_width=True)
                else:
                    st.info("No ad creative uploaded. Rule uses default text evaluation.")
            with v_col2:
                st.markdown("**Landing Page Primary Imagery**")
                if res["page_pics"]:
                    st.image([im for _, im in res["page_pics"][:3]], width=160)
                else:
                    st.info("No primary imagery found on the landing page.")
                    
            st.markdown(render_color_palette_comparison(res["ad_palette"], res["page_palette"], res["color_harmony"]), unsafe_allow_html=True)

        # TAB 3: Regulatory & Dark Patterns
        with tab_compliance:
            st.markdown("#### **Regulatory Compliance & Truth-in-Advertising Screening**")
            if not res["compliance_findings"]:
                st.success("✅ **No regulatory infractions or deceptive dark patterns detected.** The offer aligns with standard FTC and ASCI guidelines.")
            else:
                for f in res["compliance_findings"]:
                    sev_bg = "#dc2626" if f["severity"] == "Critical" else ("#ea580c" if f["severity"] == "High" else "#d97706")
                    st.markdown(f"""
                    <div style="border: 1px solid #fee2e2; border-left: 5px solid {sev_bg}; background: #fff5f5;
                                border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color: #991b1b; font-size: 1.02rem;">{f['type']}</strong>
                            <span style="background:{sev_bg}; color:#fff; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:6px;">{f['severity']}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #7f1d1d; margin: 4px 0;"><strong>Framework:</strong> {f['framework']} &bull; <strong>Trigger:</strong> {f['trigger']}</div>
                        <div style="font-size: 0.92rem; color: #1e293b; margin: 6px 0;">{f['finding']}</div>
                        <div style="background:#eff6ff; border-left:3px solid #3b82f6; padding:8px 12px; border-radius:6px; color:#1e40af; font-size:0.88rem; margin-top:8px;">
                            <strong>Mandatory Remediation:</strong> {f['recommendation']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # TAB 4: AI Copy Remediation
        with tab_remed:
            st.markdown("#### **Actionable Remediation & Synchronization Directives**")
            r_col1, r_col2 = st.columns([1, 1], gap="large")
            with r_col1:
                st.markdown("**Recommended Ad Copy Alternatives:**")
                for i, v in enumerate(res["remediation"]["ad_variants"], 1):
                    st.markdown(f"""
                    <div class='remed-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <strong>Variant {i}: {v['style']}</strong>
                            <span style='background:#e0e7ff; color:#4338ca; font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:999px;'>{v['badge']}</span>
                        </div>
                        <div style='font-size:0.95rem; font-weight:700; color:#1e293b; margin: 6px 0 2px 0;'>{v['headline']}</div>
                        <div style='font-size:0.88rem; color:#475569;'>{v['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with r_col2:
                st.markdown("**Landing Page Adjustments (Above the fold):**")
                for p in res["remediation"]["page_recommendations"]:
                    st.markdown(f"""
                    <div class='remed-card' style='border-left: 4px solid #4f46e5;'>
                        <div style='font-weight:700; font-size:0.95rem; color:#1e293b;'>📍 {p['target_zone']} &bull; {p['action']}</div>
                        <div style='font-size:0.88rem; color:#334155; margin:6px 0;'>{p['recommendation']}</div>
                        <small style='color:#16a34a; font-weight:600;'>📈 Expected Impact: {p['benefit']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        # TAB 5: Live Mockup
        with tab_preview:
            st.markdown("#### **Ad Creative Preview & Scent Continuity**")
            st.markdown(render_ad_mockup(res["ad_format"], res["brand"], res["ad_copy"], res["url"]), unsafe_allow_html=True)

        # TAB 6: Diagnostic Charts
        with tab_charts:
            st.markdown("#### **Diagnostic Performance Visualizations**")
            ch_col1, ch_col2 = st.columns(2)
            with ch_col1:
                st.markdown("**Audit Dimension Radar**")
                st.plotly_chart(create_radar_chart(res), use_container_width=True)
            with ch_col2:
                st.markdown("**Claim Verification Distribution**")
                st.plotly_chart(create_claims_donut(res["rows"]), use_container_width=True)

        # TAB 7: Exports
        with tab_exports:
            st.markdown("#### **Enterprise Report Downloads**")
            st.write("Export complete audit documentation in executive PDF, multi-sheet Excel workbook, interactive standalone HTML, or CSV format.")
            
            exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)
            with exp_c1:
                pdf_bytes = generate_pdf_report(res)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"MessageMatch_Audit_{res['brand'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with exp_c2:
                excel_bytes = generate_excel_report(res)
                st.download_button(
                    label="📊 Download Excel Workbook",
                    data=excel_bytes,
                    file_name=f"MessageMatch_Audit_{res['brand'].replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with exp_c3:
                html_str = generate_html_report(res)
                st.download_button(
                    label="🌐 Download Standalone HTML",
                    data=html_str,
                    file_name=f"MessageMatch_Audit_{res['brand'].replace(' ', '_')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            with exp_c4:
                df_claims = pd.DataFrame(res["rows"])
                st.download_button(
                    label="📑 Download CSV Data",
                    data=df_claims.to_csv(index=False),
                    file_name=f"MessageMatch_Claims_{res['brand'].replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )


# ==============================================================================
# VIEW 2: BATCH AUDITOR (BULK CSV RUNNER)
# ==============================================================================
elif nav_mode == "Batch Auditor (Bulk CSV)":
    st.markdown("## 📁 **Batch Auditor Suite**")
    st.write("Upload a portfolio of advertisements and landing pages to perform automated bulk audits across multiple campaigns.")
    
    # Template download
    sample_df = pd.DataFrame([
        {"Brand": "Apex Lending Solutions", "Ad_Format": "Google Search", "Ad_Copy": "Get loan in 1 day with zero fees. 4.9% APR guaranteed.", "Landing_URL": "https://www.apexlending.com"},
        {"Brand": "CloudPulse", "Ad_Format": "Meta / Instagram", "Ad_Copy": "Free 14-day trial without credit card. Instant setup.", "Landing_URL": "https://cloudpulse.io"},
        {"Brand": "Chronos Watches", "Ad_Format": "Meta / Instagram", "Ad_Copy": "Save 60% off Swiss chronographs. Free shipping.", "Landing_URL": "https://chronoswatches.com"}
    ])
    
    st.download_button("⬇️ Download CSV Template", sample_df.to_csv(index=False), "sample_batch_template.csv", "text/csv")
    
    batch_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
    if batch_file:
        try:
            if batch_file.name.endswith(".csv"):
                df_batch = pd.read_csv(batch_file)
            else:
                df_batch = pd.read_excel(batch_file)
                
            st.dataframe(df_batch.head(5), use_container_width=True)
            
            if st.button("🚀 Process Bulk Audit", type="primary"):
                results_batch = []
                bar = st.progress(0)
                total = len(df_batch)
                
                for idx, row in df_batch.iterrows():
                    brand = str(row.get("Brand", f"Brand {idx+1}"))
                    ad_copy = str(row.get("Ad_Copy", ""))
                    url = str(row.get("Landing_URL", ""))
                    ad_fmt = str(row.get("Ad_Format", "Google Search"))
                    
                    # Run lightweight evaluation
                    page_data = fetch_landing_page(url) if url.startswith("http") else {"text": url, "sections": {}}
                    claims = analyze_claims(ad_copy, page_data.get("text", ""))
                    score = compute_claim_fidelity_score(claims)
                    issues = sum(not c.get("Status", "").startswith("Supported") for c in claims)
                    
                    results_batch.append({
                        "Brand": brand,
                        "Ad Copy": ad_copy[:60] + "...",
                        "Landing URL": url,
                        "Match Score": score,
                        "Claims Checked": len(claims),
                        "Issues Flagged": issues,
                        "Status": "Passed" if score >= 80 else ("Needs Review" if score >= 50 else "High Risk")
                    })
                    bar.progress((idx + 1) / total)
                    
                df_res = pd.DataFrame(results_batch)
                st.success(f"Successfully audited {total} campaigns!")
                st.dataframe(df_res, use_container_width=True)
                st.download_button("⬇️ Download Batch Results (CSV)", df_res.to_csv(index=False), "batch_audit_results.csv", "text/csv")
        except Exception as e:
            st.error(f"Error parsing batch file: {e}")


# ==============================================================================
# VIEW 3: CAMPAIGNS & HISTORY (SQLITE ARCHIVE)
# ==============================================================================
elif nav_mode == "Campaigns & History":
    st.markdown("## 🗄️ **Historical Audit Archive & Persistence**")
    st.caption("All audits are permanently preserved in the local SQLite database.")
    
    audits = database.get_audits(limit=100)
    if not audits:
        st.info("No saved audits found. Run an audit in the Audit Studio to populate the database.")
    else:
        df_hist = pd.DataFrame(audits)
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            brand_filter = st.text_input("Filter by Brand Name:", "")
        with col_f2:
            st.metric("Total Preserved", len(audits))
            
        filtered_audits = [a for a in audits if not brand_filter or brand_filter.lower() in a["brand"].lower()]
        
        for a in filtered_audits:
            with st.container(border=True):
                c_i, c_info, c_sc, c_act = st.columns([1, 4.5, 1.5, 1.5], vertical_alignment="center")
                with c_i:
                    if a.get("ad_image_thumb"):
                        st.image(a["ad_image_thumb"], width=75)
                    else:
                        st.markdown("<div style='font-size:2.2rem;'>🎯</div>", unsafe_allow_html=True)
                with c_info:
                    st.markdown(f"**{a['brand']}** &bull; `{a['ad_format']}` &bull; <small>{a['created_at'][:16].replace('T', ' ')}</small>", unsafe_allow_html=True)
                    st.caption(f"Landing URL: {a['landing_url']}")
                    st.write(f"&ldquo;{a['ad_copy'][:120]}...&rdquo;")
                with c_sc:
                    score_col = "#16a34a" if a["overall_score"] >= 80 else ("#f59e0b" if a["overall_score"] >= 50 else "#dc2626")
                    st.markdown(f"<div style='text-align:center;'><strong style='font-size:1.4rem; color:{score_col};'>{a['overall_score']}</strong>/100<br><small>{a['status_label']}</small></div>", unsafe_allow_html=True)
                with c_act:
                    if st.button("🗑️ Delete", key=f"del_aud_{a['id']}", use_container_width=True):
                        database.delete_audit(a["id"])
                        st.rerun()


# ==============================================================================
# VIEW 4: BENCHMARK COMPARISON
# ==============================================================================
elif nav_mode == "Benchmark Comparison":
    st.markdown("## ⚖️ **A/B Benchmark & Optimization Comparison**")
    st.write("Compare two audits side-by-side to measure the impact of copywriting revisions on match fidelity and Quality Score.")
    
    audits = database.get_audits(limit=50)
    if len(audits) < 2:
        st.warning("Please execute at least two audits to unlock side-by-side benchmark comparison.")
    else:
        audit_options = {f"#{a['id']} - {a['brand']} ({a['overall_score']}/100) - {a['created_at'][:10]}": a["id"] for a in audits}
        col_ab1, col_ab2 = st.columns(2)
        with col_ab1:
            sel_a = st.selectbox("Select Baseline Audit (A):", list(audit_options.keys()), index=0)
        with col_ab2:
            sel_b = st.selectbox("Select Optimized Audit (B):", list(audit_options.keys()), index=min(1, len(audit_options)-1))
            
        audit_a = database.get_audit_by_id(audit_options[sel_a])
        audit_b = database.get_audit_by_id(audit_options[sel_b])
        
        if audit_a and audit_b:
            score_delta = audit_b["overall_score"] - audit_a["overall_score"]
            qs_delta = audit_b["quality_score"] - audit_a["quality_score"]
            issues_delta = audit_b["issues_count"] - audit_a["issues_count"]
            
            st.markdown("### **Performance Delta**")
            d1, d2, d3 = st.columns(3)
            d1.metric("Match Score Delta", f"{audit_b['overall_score']}%", f"{score_delta:+}%")
            d2.metric("Google Quality Score Delta", f"{audit_b['quality_score']}/10", f"{qs_delta:+.1f}")
            d3.metric("Discrepancies Resolved", f"{audit_b['issues_count']}", f"{issues_delta:+}", delta_color="inverse")
            
            c_a, c_b = st.columns(2, gap="large")
            with c_a:
                st.markdown(f"#### **Audit A: {audit_a['brand']}**")
                st.markdown(render_score_ring(audit_a["overall_score"], "Baseline Score"), unsafe_allow_html=True)
                st.write(f"**Ad Copy:** {audit_a['ad_copy']}")
            with c_b:
                st.markdown(f"#### **Audit B: {audit_b['brand']}**")
                st.markdown(render_score_ring(audit_b["overall_score"], "Optimized Score"), unsafe_allow_html=True)
                st.write(f"**Ad Copy:** {audit_b['ad_copy']}")


# ==============================================================================
# VIEW 5: RULE & COMPLIANCE ENGINE CONFIG
# ==============================================================================
elif nav_mode == "Rule & Compliance Engine":
    st.markdown("## ⚙️ **Rule & Regulatory Configuration**")
    st.write("Inspect and customize regex patterns, discrepancy severity mappings, and compliance modules.")
    
    st.markdown("### **Active Category Verification Rules**")
    for cat_name, meta in config.CLAIM_RULES.items():
        with st.expander(f"📁 {cat_name} (Severity: {meta['severity']})", expanded=False):
            st.write(f"**Description:** {meta['description']}")
            st.code(meta["pattern"], language="regex")
            
    st.markdown("### **Regulatory & FTC Dark Pattern Patterns**")
    for reg_name, pat in config.REGULATORY_PATTERNS.items():
        with st.expander(f"⚖️ {reg_name}", expanded=False):
            st.code(pat, language="regex")


# ==============================================================================
# VIEW 6: INTERACTIVE SANDBOX
# ==============================================================================
elif nav_mode == "Interactive Sandbox":
    st.markdown("## 🧪 **Interactive Testing Sandbox**")
    st.write("Quickly experiment with arbitrary claim phrases to observe how the regex and location matching engine classifies them.")
    
    test_claim = st.text_input("Enter Claim to Test:", "No hidden fees, 100% risk-free")
    test_page = st.text_area("Enter Target Context:", "Our loans carry no hidden fees. Administrative processing fee of 2% applies in footer.")
    
    if st.button("Evaluate Match Logic"):
        res_test = analyze_claims(test_claim, test_page)
        st.write(f"Found {len(res_test)} claims:")
        for r in res_test:
            st.markdown(render_claim_card(r), unsafe_allow_html=True)
