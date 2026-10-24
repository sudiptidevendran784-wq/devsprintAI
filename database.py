"""
SQLite Persistence Layer for MessageMatch Enterprise.
Manages audits, campaigns, batch jobs, and historical compliance data.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "messagematch.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_uuid TEXT UNIQUE,
        created_at TEXT,
        brand TEXT,
        ad_copy TEXT,
        landing_url TEXT,
        ad_format TEXT,
        overall_score INTEGER,
        quality_score REAL,
        visual_score REAL,
        regulatory_score REAL,
        claims_count INTEGER,
        issues_count INTEGER,
        status_label TEXT,
        ad_image_thumb TEXT,
        report_data TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        created_at TEXT,
        description TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_audit(
    audit_uuid: str,
    brand: str,
    ad_copy: str,
    landing_url: str,
    ad_format: str,
    overall_score: int,
    quality_score: float,
    visual_score: float,
    regulatory_score: float,
    claims_count: int,
    issues_count: int,
    status_label: str,
    ad_image_thumb: Optional[str],
    report_data: Dict[str, Any]
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
    INSERT OR REPLACE INTO audits (
        audit_uuid, created_at, brand, ad_copy, landing_url, ad_format,
        overall_score, quality_score, visual_score, regulatory_score,
        claims_count, issues_count, status_label, ad_image_thumb, report_data
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_uuid,
        created_at,
        brand or "Unknown Brand",
        ad_copy,
        landing_url or "(Manual text)",
        ad_format,
        overall_score,
        quality_score,
        visual_score,
        regulatory_score,
        claims_count,
        issues_count,
        status_label,
        ad_image_thumb,
        json.dumps(report_data)
    ))
    conn.commit()
    audit_id = cursor.lastrowid
    conn.close()
    return audit_id

def get_audits(limit: int = 50, brand_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM audits"
    params = []
    if brand_filter:
        query += " WHERE brand LIKE ?"
        params.append(f"%{brand_filter}%")
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

def get_audit_by_id(audit_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audits WHERE id = ?", (audit_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["report_data"] = json.loads(d["report_data"])
        return d
    return None

def delete_audit(audit_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(overall_score), AVG(quality_score), SUM(issues_count) FROM audits")
    row = cursor.fetchone()
    conn.close()
    if row and row[0] > 0:
        return {
            "total_audits": row[0],
            "avg_overall_score": round(row[1] or 0, 1),
            "avg_quality_score": round(row[2] or 0, 1),
            "total_issues_flagged": row[3] or 0
        }
    return {
        "total_audits": 0,
        "avg_overall_score": 0.0,
        "avg_quality_score": 0.0,
        "total_issues_flagged": 0
    }

# Initialize on load
init_db()
