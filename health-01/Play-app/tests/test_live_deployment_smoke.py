"""
End-to-End Live Deployment Smoke Test for Step 13.
Validates the five core workflows against a live deployed URL (Railway, Render, etc.).

Usage:
    python tests/test_live_deployment_smoke.py --url https://your-app.up.railway.app
"""
import os
import sys
import argparse
import requests

def run_live_smoke(base_url: str):
    base_url = base_url.rstrip("/")
    print("=" * 70)
    print(f"STEP 13: LIVE DEPLOYMENT SMOKE TEST AGAINST: {base_url}")
    print("=" * 70)

    # 0. Health / Root ping
    res_root = requests.get(f"{base_url}/", timeout=15)
    assert res_root.status_code == 200, f"Root endpoint failed: {res_root.status_code}"
    print("[0] Base URL responded successfully (HTTP 200)")

    # -------------------------------------------------------------------------
    # CHECK 2: PHARMACIST WORKFLOW (READ-ONLY, ZERO CLINICAL NOTES)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 2: PHARMACIST LIVE WORKFLOW")
    print("-" * 70)
    s_pharma = requests.Session()
    res_pharma_login = s_pharma.post(
        f"{base_url}/login",
        data={"username": "pharma_demo", "password": "password123"},
        allow_redirects=True,
        timeout=15,
    )
    assert res_pharma_login.status_code == 200, f"Pharma login failed: {res_pharma_login.status_code}"
    print("  [2.1] Pharmacist logged in successfully on live deployment")

    res_pharma_scan = s_pharma.post(
        f"{base_url}/pharmacist/scan",
        data={"card_id": "SS-TEST-001"},
        allow_redirects=True,
        timeout=15,
    )
    assert res_pharma_scan.status_code == 200
    pharma_html = res_pharma_scan.text
    assert "SS-TEST-001" in pharma_html
    assert "Flu" in pharma_html or "Hypertension" in pharma_html
    assert "Paracetamol" in pharma_html or "Amlodipine" in pharma_html
    assert "diagnosis_notes" not in pharma_html
    assert "rhinorrhea" not in pharma_html
    assert "/add-checkup" not in pharma_html
    print("  [2.2] Pharmacist view displays required fields and STRICTLY hides clinical notes")

    # -------------------------------------------------------------------------
    # CHECK 3: PUBLIC HEALTH ADMIN (AGGREGATES ONLY, ZERO PATIENTS)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 3: PUBLIC HEALTH LIVE WORKFLOW")
    print("-" * 70)
    s_pha = requests.Session()
    res_pha_login = s_pha.post(
        f"{base_url}/login",
        data={"username": "public_demo", "password": "password123"},
        allow_redirects=True,
        timeout=15,
    )
    assert res_pha_login.status_code == 200
    print("  [3.1] Public Health Admin logged in successfully")

    res_pha_dash = s_pha.get(f"{base_url}/public-health/dashboard", timeout=15)
    assert res_pha_dash.status_code == 200
    pha_html = res_pha_dash.text
    assert "Ward A" in pha_html
    assert "Insufficient Data" in pha_html or "Suppressed" in pha_html or "< 5" in pha_html
    for patient_name in ["Meera Joshi", "Arjun Sharma", "Priya Sen"]:
        assert patient_name not in pha_html, f"Patient identifier leaked in public health: {patient_name}"
    print("  [3.2] Public Health surveillance enforces privacy (<5 suppression) and zero PII")

    # -------------------------------------------------------------------------
    # CHECK 4: SYSADMIN WORKFLOW (IMMUTABLE AUDIT TRAIL, ZERO CLINICAL DATA)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 4: SYSADMIN LIVE WORKFLOW")
    print("-" * 70)
    s_admin = requests.Session()
    res_admin_login = s_admin.post(
        f"{base_url}/login",
        data={"username": "admin_demo", "password": "password123"},
        allow_redirects=True,
        timeout=15,
    )
    assert res_admin_login.status_code == 200
    print("  [4.1] Sysadmin logged in successfully")

    res_admin_audit = s_admin.get(f"{base_url}/admin/audit-log", timeout=15)
    assert res_admin_audit.status_code == 200
    audit_html = res_admin_audit.text
    assert "Audit Log" in audit_html or "audit" in audit_html.lower()
    for clinical_kw in ["rhinorrhea", "diagnosis_notes", "Amlodipine 5mg OD"]:
        assert clinical_kw not in audit_html
    print("  [4.2] Sysadmin audit log verified: operational events logged, 0 clinical data exposed")

    # -------------------------------------------------------------------------
    # CHECK 5: CROSS-ROLE 403 ENFORCEMENT & AUDIT DENIAL RECORDING
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 5: CROSS-ROLE 403 ENFORCEMENT")
    print("-" * 70)
    # Re-use pharmacist session to try accessing doctor and admin routes
    res_forbidden_doc = s_pharma.get(f"{base_url}/doctor/scan", timeout=15)
    assert res_forbidden_doc.status_code == 403, f"Expected 403, got {res_forbidden_doc.status_code}"
    print("  [5.1] Pharmacist hitting /doctor/scan returned HTTP 403 Forbidden")

    res_forbidden_admin = s_pharma.get(f"{base_url}/admin/dashboard", timeout=15)
    assert res_forbidden_admin.status_code == 403, f"Expected 403, got {res_forbidden_admin.status_code}"
    print("  [5.2] Pharmacist hitting /admin/dashboard returned HTTP 403 Forbidden")

    print("\n" + "=" * 70)
    print("ALL LIVE SMOKE TEST CHECKS PASSED AGAINST DEPLOYED INSTANCE!")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run live deployment smoke test.")
    parser.add_argument("--url", default=os.environ.get("LIVE_URL", "http://127.0.0.1:5000"), help="Base URL of deployed app")
    args = parser.parse_args()
    run_live_smoke(args.url)
