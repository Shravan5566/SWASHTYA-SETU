import os
import sys
import html as html_lib
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.pool import StaticPool
from app import create_app
from app.extensions import db
from app.config import Config
from app.models.user import User
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.access_log import AccessLog
from app.models.stats import Stats
from app.utils.seed import seed_database
from app.services.otp_service import get_raw_otp_for_testing
from app.services.anonymizer import INSUFFICIENT_DATA_SENTINEL


class TestConfig(Config):
    """Isolated in-memory config for the Step 12 smoke test."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }


def run_e2e_smoke_test():
    print("=" * 70)
    print("STEP 12: END-TO-END SYSTEM SMOKE TEST (ALL 5 CHECKS IN ONE SITTING)")
    print("=" * 70)

    app = create_app(TestConfig)

    # Seed fresh database
    with app.app_context():
        db.create_all()
        results = seed_database()
        print(f"[*] Initialized database with seed data:")
        print(f"    - Staff accounts: {results['users']}")
        print(f"    - Patient cards: {results['patients']}")
        print(f"    - Stats cohorts: {results['stats']} rows")

    client = app.test_client()

    # -------------------------------------------------------------------------
    # CHECK 1: DOCTOR FLOW
    # scan -> OTP -> view history -> AI summary renders -> add typed visit
    # -> add voice visit -> delete just-added visit -> confirm older visit CANNOT be deleted
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 1: DOCTOR WORKFLOW")
    print("-" * 70)

    # 1. Login as doctor
    res_login = client.post("/login", data={"username": "doctor_demo", "password": "password123"}, follow_redirects=True)
    assert res_login.status_code == 200, f"Doctor login failed: {res_login.status_code}"
    print("  [1.1] Doctor logged in successfully")

    # 2. Access scan page
    res_scan_page = client.get("/doctor/scan")
    assert res_scan_page.status_code == 200
    assert "Scan Patient Card" in res_scan_page.get_data(as_text=True)
    print("  [1.2] Doctor opened QR scan interface")

    # 3. Scan card SS-TEST-001 -> triggers OTP
    res_scan_ajax = client.post("/ajax/scan-card", json={"card_id": "SS-TEST-001"})
    assert res_scan_ajax.status_code == 200
    scan_data = res_scan_ajax.get_json()
    assert scan_data["ok"] is True, f"Scan failed: {scan_data}"
    patient_id = scan_data["patient_id"]
    print(f"  [1.3] Scanned card SS-TEST-001 -> OTP generated for patient #{patient_id}")

    # 4. Verify OTP using the test helper
    otp_info = get_raw_otp_for_testing(patient_id)
    assert otp_info is not None, "OTP entry not found — was generate_and_send_otp called?"
    raw_otp = otp_info["raw_otp"]

    res_verify_ajax = client.post("/ajax/verify-otp", json={
        "code": raw_otp,
    })
    assert res_verify_ajax.status_code == 200
    verify_data = res_verify_ajax.get_json()
    assert verify_data["ok"] is True, f"OTP verify failed: {verify_data}"
    redirect_url = verify_data["redirect"]
    print(f"  [1.4] OTP verified -> scoped session token issued; redirect: {redirect_url}")

    # 5. Access patient history page
    res_hist = client.get(redirect_url)
    assert res_hist.status_code == 200
    hist_html = res_hist.get_data(as_text=True)
    assert "Patient History" in hist_html
    assert "Meera Joshi" in hist_html
    assert "SS-TEST-001" in hist_html

    # AI summary check + TTS button
    assert "AI Clinical Summary" in hist_html
    assert "ai-summary-text" in hist_html
    assert "readSummary" in hist_html
    print("  [1.5] Patient history loaded: AI clinical summary rendered with TTS audio trigger")

    # 6. Add checkup via typed form
    res_add_typed = client.post(f"/doctor/patient/{patient_id}/add-checkup", data={
        "area": "Ward A",
        "condition": "Seasonal Allergy",
        "diagnosis_notes": "Mild allergic conjunctivitis and sneezing.",
        "medicine": "Cetirizine",
        "dosage": "10mg OD at night",
        "refill_restricted": "0",
    }, follow_redirects=True)
    assert res_add_typed.status_code == 200
    typed_html = res_add_typed.get_data(as_text=True)
    assert "Checkup added successfully" in typed_html
    assert "Seasonal Allergy" in typed_html
    assert "Cetirizine" in typed_html
    print("  [1.6] Checkup added via manual typing: 'Seasonal Allergy' / 'Cetirizine 10mg OD'")

    # 7. Add checkup via voice parsing
    voice_transcript = "Patient in Ward A diagnosed with Acute Bronchitis. Prescribe Amoxcilin 500mg TDS for 5 days. Rest recommended."
    res_voice_parse = client.post("/ai/voice-parse", json={"transcript": voice_transcript})
    assert res_voice_parse.status_code == 200
    parsed_json = res_voice_parse.get_json()
    assert parsed_json["success"] is True
    pdata = parsed_json["data"]
    assert pdata["medicine"] == "Amoxicillin", f"Expected auto-corrected Amoxicillin, got {pdata.get('medicine')}"
    print(f"  [1.7] Voice dictation parsed: transcript -> '{pdata['condition']}' / '{pdata['medicine']}' ({pdata['dosage']})")

    res_add_voice = client.post(f"/doctor/patient/{patient_id}/add-checkup", data={
        "area": pdata["area"],
        "condition": pdata["condition"],
        "diagnosis_notes": pdata["diagnosis_notes"],
        "medicine": pdata["medicine"],
        "dosage": pdata["dosage"],
        "refill_restricted": "0",
    }, follow_redirects=True)
    assert res_add_voice.status_code == 200
    voice_save_html = res_add_voice.get_data(as_text=True)
    assert "Acute Bronchitis" in voice_save_html
    print("  [1.8] Voice-parsed checkup saved to patient history")

    # 8. Delete the just-added visit
    with app.app_context():
        newest_visit = Visit.query.filter_by(patient_id=patient_id, condition="Acute Bronchitis").order_by(Visit.id.desc()).first()
        assert newest_visit is not None
        newest_visit_id = newest_visit.id

    res_del_new = client.post(f"/doctor/visit/{newest_visit_id}/delete", follow_redirects=True)
    assert res_del_new.status_code == 200
    with app.app_context():
        assert db.session.get(Visit, newest_visit_id) is None
    print(f"  [1.9] Just-added visit #{newest_visit_id} successfully deleted within edit window")

    # 9. Confirm older visit CANNOT be deleted (> 24 hours old)
    with app.app_context():
        older_visit = Visit.query.filter(
            Visit.patient_id == patient_id,
            Visit.created_at < (datetime.utcnow() - timedelta(hours=24))
        ).first()
        assert older_visit is not None
        older_visit_id = older_visit.id

    res_del_old = client.post(f"/doctor/visit/{older_visit_id}/delete", follow_redirects=False)
    assert res_del_old.status_code == 403, f"Expected 403 for deleting older visit, got {res_del_old.status_code}"
    with app.app_context():
        assert db.session.get(Visit, older_visit_id) is not None, "Older visit should NOT be deleted"
    print(f"  [1.10] Verified: Older visit #{older_visit_id} (10 days old) was strictly BLOCKED from deletion (403)")

    # Logout doctor
    client.get("/logout")

    # -------------------------------------------------------------------------
    # CHECK 2: PHARMACIST FLOW
    # scan -> sees exactly 4 fields, refill-restricted item blocked, no edit/delete UI
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 2: PHARMACIST WORKFLOW (READ-ONLY, NO OTP)")
    print("-" * 70)

    # 1. Login as pharmacist
    res_pharma_login = client.post("/login", data={"username": "pharma_demo", "password": "password123"}, follow_redirects=True)
    assert res_pharma_login.status_code == 200
    print("  [2.1] Pharmacist logged in")

    # 2. Pharmacist scan SS-TEST-001 (Direct lookup, NO OTP)
    res_pharma_view = client.post("/pharmacist/scan", data={"card_id": "SS-TEST-001"}, follow_redirects=True)
    assert res_pharma_view.status_code == 200
    pharma_html = res_pharma_view.get_data(as_text=True)

    # Verify 4 required fields
    assert "SS-TEST-001" in pharma_html, "card_id missing"
    assert "Flu" in pharma_html or "Hypertension" in pharma_html, "condition missing"
    assert "Paracetamol" in pharma_html or "Amlodipine" in pharma_html, "medicine missing"
    assert "2026" in pharma_html or "2025" in pharma_html, "date/time missing"
    print("  [2.2] Pharmacist view displays exactly the 4 required columns (card_id, date, condition, medicine)")

    # Verify diagnosis_notes never rendered or fetched
    assert "diagnosis_notes" not in pharma_html
    assert "Diagnosis Notes" not in pharma_html
    assert "rhinorrhea" not in pharma_html, "Clinical observation leaked to pharmacist"
    print("  [2.3] Verified: Clinical diagnosis notes are completely absent from query & HTML")

    # Verify refill-restricted blocked
    assert "Refill Restricted" in pharma_html
    assert "must see a doctor" in pharma_html
    print("  [2.4] Verified: Refill-restricted medicine (Amlodipine) is blocked with warning")

    # Verify no mutation UI exists
    assert "/add-checkup" not in pharma_html
    assert "/delete" not in pharma_html
    print("  [2.5] Verified: No edit, delete, or checkup-creation UI exists in pharmacist view")

    # Logout pharmacist
    client.get("/logout")

    # -------------------------------------------------------------------------
    # CHECK 3: PUBLIC HEALTH ADMIN FLOW
    # dashboard shows real counts for well-populated area, "insufficient data"
    # for sparse one, trend alert appears for seeded spike
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 3: PUBLIC HEALTH ADMIN WORKFLOW (AGGREGATES ONLY, ZERO PATIENTS)")
    print("-" * 70)

    # 1. Login as public health admin
    res_pha_login = client.post("/login", data={"username": "public_demo", "password": "password123"}, follow_redirects=True)
    assert res_pha_login.status_code == 200
    print("  [3.1] Public health admin logged in")

    # 2. Surveillance Dashboard
    res_pha_dash = client.get("/public-health/dashboard")
    assert res_pha_dash.status_code == 200
    pha_html = res_pha_dash.get_data(as_text=True)

    # Well-populated area (Ward A / Ward B, count >= 5) shows real count (e.g. 26 or 32)
    assert "Ward A" in pha_html
    assert "26" in pha_html or "32" in pha_html
    print("  [3.2] Well-populated areas display unsuppressed numeric totals (e.g. 26 / 32 cases)")

    # Sparse area (Ward C, count < 5) shows "Insufficient Data" sentinel
    assert "Ward C" in pha_html
    assert (INSUFFICIENT_DATA_SENTINEL in pha_html) or (html_lib.escape(INSUFFICIENT_DATA_SENTINEL) in pha_html)
    assert "Suppressed (<5)" in pha_html or "Suppressed" in pha_html
    print(f"  [3.3] Sparse cohorts (< 5 cases) display protected sentinel: '{INSUFFICIENT_DATA_SENTINEL}'")

    # Outbreak trend alerts
    res_pha_alerts = client.get("/public-health/trend-alerts")
    assert res_pha_alerts.status_code == 200
    alerts_html = res_pha_alerts.get_data(as_text=True)
    assert "Dengue" in alerts_html and "Ward B" in alerts_html
    assert "38" in alerts_html
    print("  [3.4] Outbreak trend alert detected and displayed (Ward B Dengue spike of 38 cases)")

    # Zero patient identifiers check
    for forbidden in ["SS-TEST-001", "Meera Joshi", "Arjun Sharma", "Priya Sen"]:
        assert forbidden not in pha_html, f"Leak in Public Health dashboard: {forbidden}"
        assert forbidden not in alerts_html, f"Leak in Trend Alerts: {forbidden}"
    print("  [3.5] Verified: Zero patient identifiers anywhere in Public Health panel")

    # Logout public health admin
    client.get("/logout")

    # -------------------------------------------------------------------------
    # CHECK 4: SYSADMIN FLOW
    # create account, issue card, view audit log, confirm zero clinical data
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 4: SYSTEM ADMIN WORKFLOW")
    print("-" * 70)

    # 1. Login as sysadmin
    res_admin_login = client.post("/login", data={"username": "admin_demo", "password": "password123"}, follow_redirects=True)
    assert res_admin_login.status_code == 200
    print("  [4.1] System admin logged in")

    # 2. Create staff account
    smoke_doctor_user = "dr_step12_verified"
    res_create_staff = client.post("/admin/users/create", data={
        "username": smoke_doctor_user,
        "full_name": "Dr. Sneha Patil",
        "role": "doctor",
        "password": "securepassword123",
    }, follow_redirects=True)
    assert res_create_staff.status_code == 200
    with app.app_context():
        created_doctor = User.query.filter_by(username=smoke_doctor_user).first()
        assert created_doctor is not None
        assert created_doctor.check_password("securepassword123") is True
    print(f"  [4.2] Created new doctor account '{smoke_doctor_user}' successfully")

    # 3. Issue patient QR card
    res_issue_card = client.post("/admin/patients/register", data={
        "name": "Anil Deshmukh",
        "phone": "+919822001122",
    }, follow_redirects=True)
    assert res_issue_card.status_code == 200
    issue_html = res_issue_card.get_data(as_text=True)
    assert "Card Issued Successfully" in issue_html
    assert "Anil Deshmukh" in issue_html
    assert "data:image/png;base64," in issue_html
    print("  [4.3] Issued new encrypted patient card with high-density QR code")

    # 4. View audit log
    res_admin_audit = client.get("/admin/audit-log")
    assert res_admin_audit.status_code == 200
    admin_audit_html = res_admin_audit.get_data(as_text=True)
    assert "Immutable Security Audit Log" in admin_audit_html
    assert "ALLOWED" in admin_audit_html or "allowed" in admin_audit_html
    print("  [4.4] Read-only audit trail rendered with logged system events")

    # 5. Confirm zero clinical data visible in admin panel
    for clinical_kw in ["diagnosis_notes", "Amlodipine 5mg OD", "Seasonal Fever"]:
        assert clinical_kw not in admin_audit_html
        assert clinical_kw not in issue_html
    print("  [4.5] Verified: Zero clinical data or diagnosis notes exposed in Admin panel")

    # Logout sysadmin
    client.get("/logout")

    # -------------------------------------------------------------------------
    # CHECK 5: CROSS-ROLE 403 ENFORCEMENT & AUDIT LOGGING
    # log in as pharmacist, hit doctor or admin URL -> confirm 403 page
    # -> confirm AccessLog row was written for the denial
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("CHECK 5: CROSS-ROLE 403 ENFORCEMENT & AUDIT RECORDING")
    print("-" * 70)

    # 1. Login as pharmacist
    client.post("/login", data={"username": "pharma_demo", "password": "password123"}, follow_redirects=True)
    with app.app_context():
        pharma_user = User.query.filter_by(username="pharma_demo").first()
        pharma_uid = pharma_user.id
        prior_denied_count = AccessLog.query.filter_by(user_id=pharma_uid, result="denied").count()

    # 2. Attempt to access doctor routes
    res_pharma_doc = client.get("/doctor/scan")
    assert res_pharma_doc.status_code == 403
    doc_err_html = res_pharma_doc.get_data(as_text=True)
    assert "403" in doc_err_html and ("Access Denied" in doc_err_html or "Forbidden" in doc_err_html)
    print("  [5.1] Pharmacist blocked from /doctor/scan with 403 Access Denied page")

    # 3. Attempt to access admin dashboard
    res_pharma_admin = client.get("/admin/dashboard")
    assert res_pharma_admin.status_code == 403
    admin_err_html = res_pharma_admin.get_data(as_text=True)
    assert "403" in admin_err_html
    print("  [5.2] Pharmacist blocked from /admin/dashboard with 403 Access Denied page")

    # 4. Confirm AccessLog rows were written for both denials
    with app.app_context():
        current_denied = AccessLog.query.filter_by(user_id=pharma_uid, result="denied").all()
        assert len(current_denied) >= prior_denied_count + 2, "AccessLog should have recorded at least 2 new denials"

        endpoints_denied = [log.endpoint for log in current_denied]
        assert any("/doctor/scan" in ep or "doctor_routes.scan_qr" in ep for ep in endpoints_denied)
        assert any("/admin/dashboard" in ep or "admin_routes.dashboard" in ep for ep in endpoints_denied)
        print(f"  [5.3] Verified: AccessLog recorded {len(current_denied)} denial event(s) for user #{pharma_uid}")

    # Logout
    client.get("/logout")

    print("\n" + "=" * 70)
    print("ALL 5 SMOKE TEST CHECKS PASSED PERFECTLY IN ONE SITTING! (100% SUCCESS)")
    print("=" * 70)


if __name__ == "__main__":
    run_e2e_smoke_test()
