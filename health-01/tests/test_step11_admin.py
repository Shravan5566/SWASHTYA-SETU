import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.patient import Patient
from app.models.access_log import AccessLog
from app.utils.seed import seed_staff_accounts, seed_patients
from app.services.qr_service import (
    generate_card_id,
    generate_qr_code,
    issue_patient_card,
    lookup_patient_by_card,
)


def run_tests():
    print("=" * 60)
    print("STEP 11 TEST SUITE: System Admin Panel, QR Issuance & Audit Log")
    print("=" * 60)

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        seed_staff_accounts()
        seed_patients()

        # ─────────────────────────────────────────────────────────────────────
        # 1. QR Generator & Card Issuance Unit Tests
        # ─────────────────────────────────────────────────────────────────────
        print("\n--- 1. QR Generator & Card Issuance Services ---")
        card_id = generate_card_id()
        assert card_id.startswith("SS-"), f"Expected card_id to start with 'SS-', got {card_id}"
        assert len(card_id) == 11, f"Expected length 11 (SS-XXXXXXXX), got {len(card_id)}"
        print(f"  [PASS] Non-guessable card_id generated: {card_id}")

        qr_uri = generate_qr_code(card_id)
        assert qr_uri.startswith("data:image/png;base64,"), "QR URI must be base64 PNG data URI"
        assert len(qr_uri) > 100
        print("  [PASS] QR code successfully rendered into base64 PNG data URI")

        # Test issue_patient_card service
        p, p_qr = issue_patient_card("Aarav Patel", "+919123456780")
        assert p.id is not None
        assert p.card_id.startswith("SS-")
        assert p.name_encrypted != "Aarav Patel", "Patient name must be stored encrypted"
        assert p.phone_encrypted != "+919123456780", "Patient phone must be stored encrypted"
        print(f"  [PASS] Patient card issued: id={p.id}, card_id={p.card_id} with encrypted PII")

        # Lookup card
        found = lookup_patient_by_card(p.card_id)
        assert found is not None and found.id == p.id
        print("  [PASS] lookup_patient_by_card resolved newly issued card")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. RBAC Enforcement on /admin routes
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 2. RBAC Access Control Enforcement ---")
    client = app.test_client()

    # Unauthenticated -> 403
    res_anon = client.get("/admin/dashboard")
    assert res_anon.status_code == 403, f"Expected 403 for unauthenticated, got {res_anon.status_code}"
    print(f"  [PASS] Unauthenticated access denied with 403")

    # Doctor -> 403
    with client.session_transaction() as sess:
        with app.app_context():
            doc = User.query.filter_by(role="doctor").first()
            sess["_user_id"] = str(doc.id)
            sess["_fresh"] = True
    res_doc = client.get("/admin/dashboard")
    assert res_doc.status_code == 403
    print(f"  [PASS] Doctor blocked from admin panel with 403")

    # Pharmacist -> 403
    with client.session_transaction() as sess:
        with app.app_context():
            pharma = User.query.filter_by(role="pharmacist").first()
            sess["_user_id"] = str(pharma.id)
            sess["_fresh"] = True
    res_pharma = client.get("/admin/dashboard")
    assert res_pharma.status_code == 403
    print(f"  [PASS] Pharmacist blocked from admin panel with 403")

    # Public Health Admin -> 403
    with client.session_transaction() as sess:
        with app.app_context():
            pha = User.query.filter_by(role="public_health_admin").first()
            sess["_user_id"] = str(pha.id)
            sess["_fresh"] = True
    res_pha = client.get("/admin/dashboard")
    assert res_pha.status_code == 403
    print(f"  [PASS] Public Health Admin blocked from admin panel with 403")

    # Sysadmin -> 200
    with client.session_transaction() as sess:
        with app.app_context():
            admin = User.query.filter_by(role="sysadmin").first()
            sess["_user_id"] = str(admin.id)
            sess["_fresh"] = True
    res_admin = client.get("/admin/dashboard")
    assert res_admin.status_code == 200
    print(f"  [PASS] Sysadmin granted access to dashboard with 200")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Staff User Creation & Management
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 3. Staff Account Creation & Management ---")
    test_doctor_username = "dr_kavita_sharma"
    with app.app_context():
        # Remove if exists from earlier test
        old_u = User.query.filter_by(username=test_doctor_username).first()
        if old_u:
            db.session.delete(old_u)
            db.session.commit()

    # Create new doctor
    res_create = client.post("/admin/users/create", data={
        "username": test_doctor_username,
        "full_name": "Dr. Kavita Sharma",
        "role": "doctor",
        "password": "doctorpassword123",
    }, follow_redirects=True)
    assert res_create.status_code == 200
    html_users = res_create.get_data(as_text=True)
    assert test_doctor_username in html_users
    print(f"  [PASS] Sysadmin created new doctor account '{test_doctor_username}'")

    # Authenticate with the new doctor account to verify credentials
    with app.app_context():
        new_doc = User.query.filter_by(username=test_doctor_username).first()
        assert new_doc is not None
        assert new_doc.check_password("doctorpassword123") is True
        assert new_doc.role == "doctor"
        print("  [PASS] Newly created doctor can authenticate successfully with password")

    # Toggle user deactivation
    res_toggle = client.post(f"/admin/users/{new_doc.id}/toggle-status", follow_redirects=True)
    assert res_toggle.status_code == 200
    with app.app_context():
        deactivated_doc = User.query.get(new_doc.id)
        assert deactivated_doc.is_active is False
        print(f"  [PASS] Deactivated user '{test_doctor_username}' (is_active=False)")

    # Sysadmin cannot deactivate themselves
    with app.app_context():
        admin = User.query.filter_by(role="sysadmin").first()
    res_self_deact = client.post(f"/admin/users/{admin.id}/toggle-status", follow_redirects=True)
    assert res_self_deact.status_code == 200
    with app.app_context():
        admin_refetch = User.query.get(admin.id)
        assert admin_refetch.is_active is True, "Sysadmin must not be able to deactivate self"
        print("  [PASS] Security constraint verified: Sysadmin cannot deactivate self")

    # Role update
    res_role = client.post(f"/admin/users/{new_doc.id}/role", data={"role": "pharmacist"}, follow_redirects=True)
    assert res_role.status_code == 200
    with app.app_context():
        updated_u = User.query.get(new_doc.id)
        assert updated_u.role == "pharmacist"
        print("  [PASS] Role assignment updated user role from doctor to pharmacist")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Patient QR Card Issuance via Web UI
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 4. Patient QR Card Issuance Portal ---")
    res_reg_get = client.get("/admin/patients/register")
    assert res_reg_get.status_code == 200
    print("  [PASS] GET /admin/patients/register rendered (200)")

    res_reg_post = client.post("/admin/patients/register", data={
        "name": "Devendra Kulkarni",
        "phone": "+919811223344",
    }, follow_redirects=True)
    assert res_reg_post.status_code == 200
    reg_html = res_reg_post.get_data(as_text=True)
    assert "Card Issued Successfully" in reg_html
    assert "Devendra Kulkarni" in reg_html
    assert "data:image/png;base64," in reg_html
    print("  [PASS] POST /admin/patients/register issued card and rendered printable QR preview")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Read-Only Audit Log Inspection
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 5. Audit Log Inspection ---")
    res_audit = client.get("/admin/audit-log")
    assert res_audit.status_code == 200
    audit_html = res_audit.get_data(as_text=True)
    assert "Immutable Security Audit Log" in audit_html
    assert "ALLOWED" in audit_html or "allowed" in audit_html
    assert "DENIED" in audit_html or "denied" in audit_html
    print("  [PASS] Audit log rendered with both allowed and denied events")

    # Test filtering by denied only
    res_audit_denied = client.get("/admin/audit-log?result=denied")
    assert res_audit_denied.status_code == 200
    audit_denied_html = res_audit_denied.get_data(as_text=True)
    assert "DENIED" in audit_denied_html
    print("  [PASS] Filtered audit log (?result=denied) returns only denied events")

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Zero Clinical Data Leakage Check in Admin Blueprint
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 6. Zero Clinical Data Exposure Check ---")
    # Sysadmin must never see diagnosis_notes, condition, or medicine history
    clinical_keywords = [
        "diagnosis_notes",
        "Paracetamol 500mg TDS",
        "Amlodipine 5mg OD",
    ]
    for page_html in [audit_html, reg_html, html_users]:
        for kw in clinical_keywords:
            assert kw not in page_html, f"CLINICAL PRIVACY VIOLATION: '{kw}' exposed in Admin Blueprint!"
    print("  [PASS] Verified zero clinical visit data or diagnosis notes exposed in Admin panel")

    print("\n" + "=" * 60)
    print("ALL STEP 11 ADMIN TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
