# 🎯 MessageMatch Enterprise (v2.4)
### AI-Powered Ad-to-Landing-Page Match & Regulatory Compliance Audit Suite

**MessageMatch Enterprise** is an advanced compliance and conversion-optimization platform designed for performance marketers, media buyers, brand safety officers, and legal teams. It validates whether what your advertisements promise (copy, discounts, deadlines, and visuals) is truthfully and prominently delivered on the destination landing page.

---

## 🚀 Key Capabilities

1. **Multi-Category Claim Fidelity Engine**
   - Extracts and verifies 7 categories of claims: Speed & Turnaround, Pricing & Discounts, Fees & Transparency, Free Trials, Guarantees & Safety, Financing APRs, and Exclusivity Accreditations.
   - **Zone-Aware Inspection**: Differentiates whether a claim is supported **Above the Fold (Hero/Headline)**, in the **Main Body**, or buried in **Footer Fine Print / Asterisk Disclaimers**.

2. **Offer Expiration & Deadline Integrity**
   - Extracts specific and relative promotion deadlines.
   - Flags expired dates against real-time calendar and identifies date discrepancies between ad copy and page terms.

3. **Multimodal Visual & Brand Alignment**
   - Dual perceptual hashing (`dHash` + `aHash`) for image layout comparison.
   - **Dominant Color Palette Quantization**: Extracts top hex swatches and calculates chromatic harmony percentage in Euclidean RGB space.
   - Built-in OCR text extraction with automated error handling and fallback.

4. **Regulatory, FTC & Dark Pattern Screening**
   - Screens for **FTC 16 CFR Part 255 (Truth-in-Advertising)**, **FTC Negative Option Rule (Subscription traps)**, and **ASCI / BBB** compliance.
   - Detects artificial scarcity countdowns, missing asterisk disclosures, and unverified medical health claims.

5. **Google Ads Quality Score & Auction Impact Simulator**
   - Estimates predicted Google Ads Quality Score (1-10) and Meta Relevance Diagnostics.
   - Computes estimated CPC discount (-50%) or surcharge (+400%) and calculates estimated monthly budget waste.

6. **AI Copy Remediation Engine**
   - Generates 3 synchronized ad headline/body variants (Compliance-First, CTR-Optimized, Calibrated Urgency).
   - Recommends hero section adjustments to eliminate user bounce rates.

7. **Multi-Format Enterprise Exporters**
   - 📄 **Executive PDF Audit Report** (`fpdf2`)
   - 📊 **Multi-Sheet Excel Workbook** (`openpyxl`)
   - 🌐 **Standalone Interactive HTML Report**
   - 📑 **Raw CSV Data Export**

8. **Persistent SQLite Database & Batch Suite**
   - Local database (`messagematch.db`) with full history, metrics, and search.
   - **Bulk CSV Batch Auditor** to process dozens of ad campaigns in parallel.
   - **A/B Benchmark Comparison** to measure optimization impact side-by-side.

---

## 🛠️ Architecture Overview

```
c:\Devsprint\
├── app.py                      # Streamlit application UI & navigation
├── config.py                   # Rules, regex patterns, regulatory frameworks
├── database.py                 # SQLite database persistence layer
├── demo_data.py                # Preloaded enterprise demo scenarios
├── seed_db.py                  # Database seed script with sample case studies
├── test_suite.py               # Integration test suite
├── requirements.txt            # Python dependencies
├── core/
│   ├── scraper.py              # Web scraper & section segmenter (Hero vs Footer)
│   ├── claim_engine.py         # Category claim & deadline verification
│   ├── visual_engine.py        # Perceptual hash, palette extraction & OCR
│   ├── compliance_engine.py    # FTC, ASCI & Dark pattern auditor
│   ├── quality_score.py        # Quality Score & CPC impact estimator
│   ├── remediation.py          # Copy rewrite & synchronization generator
│   └── search.py               # DuckDuckGo domain discovery engine
├── components/
│   ├── ui_cards.py             # Custom HTML cards, badges & score rings
│   ├── charts.py               # Plotly radar and donut diagnostic charts
│   └── diff_viewer.py          # Google/Meta ad mockups & palette swatches
└── exporters/
    ├── pdf_exporter.py         # PDF generation (fpdf2)
    ├── excel_exporter.py       # Styled Excel workbook (openpyxl)
    └── html_exporter.py        # Self-contained HTML report
```

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```
Then navigate to `http://localhost:8501` in your browser.

### 3. Run Integration Tests
```bash
python test_suite.py
```

---

## 🧪 Pre-Configured Demo Scenarios

In **Audit Studio**, open the *⚡ Load Pre-Configured Enterprise Demo Scenarios* dropdown to test:
- **FinTech Loan Approval**: Analyzes 1-day turnaround and zero-fee claims vs buried 5% origination fee disclaimers.
- **B2B SaaS Free Trial**: Detects hidden credit card auto-renewal subscription traps.
- **E-Commerce Flash Sale**: Evaluates 60% off flash sales against real catalog discounts.
- **Health & Wellness**: Screens unverified medical cure promises against statutory FDA/DSHEA requirements.
