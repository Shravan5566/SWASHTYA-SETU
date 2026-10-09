import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.visit import Visit
from app.models.patient import Patient
from app.utils.seed import seed_staff_accounts, seed_patients
from app.services.qr_service import lookup_patient_by_card
from app.services.otp_service import generate_and_send_otp, verify_otp, validate_access_token


def run_tests():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_staff_accounts()
        seed_patients()
        print("Seeded users and patients.")

    # ── Test 1: QR service lookup ────────────────────────────────────────────
    with app.app_context():
        p = lookup_patient_by_card("SS-TEST-001")
        assert p is not None, "Patient SS-TEST-001 not found"
        none_p = lookup_patient_by_card("NONEXISTENT-CARD")
        assert none_p is None
        print(f"Test 1 - QR lookup: found patient id={p.id}")

    # ── Test 2: OTP generate, verify (correct), token validation ────────────
    with app.app_context():
        patient = lookup_patient_by_card("SS-TEST-001")
        from app.models.user import User
        doctor = User.query.filter_by(username="doctor_demo").first()

        generate_and_send_otp(patient.id, doctor.id, "+919876543210")

        # Grab the OTP directly from the store for testing
        from app.services import otp_service
        import hashlib
        entry = otp_service._otp_store.get((patient.id, doctor.id))
        assert entry is not None, "OTP not stored"

        # Simulate correct code by brute-forcing from store (only in tests)
        for code in range(1_000_000):
            test_hash = hashlib.sha256(f"{code:06d}".encode()).hexdigest()
            if test_hash == entry["code_hash"]:
                correct_code = f"{code:06d}"
                break

        # Wrong code rejected
        bad_token = verify_otp(patient.id, doctor.id, "000000")
        if bad_token is not None:  # If 000000 happened to be correct, regenerate
            generate_and_send_otp(patient.id, doctor.id, "+919876543210")
            entry = otp_service._otp_store.get((patient.id, doctor.id))

        # Correct code accepted
        token = verify_otp(patient.id, doctor.id, correct_code)
        assert token is not None, "OTP verification failed for correct code"
        print(f"Test 2 - OTP verify: token issued ({'ok' if token else 'FAIL'})")

        # Token valid for right pair
        assert validate_access_token(token, patient.id, doctor.id) is True
        # Token invalid for wrong patient
        assert validate_access_token(token, 99999, doctor.id) is False
        print("Test 3 - Token validation: correct pair=True, wrong pair=False")

    # ── Test 4: patient_history route requires valid session token ────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "doctor_demo", "password": "password123"})

        with app.app_context():
            patient = Patient.query.filter_by(card_id="SS-TEST-001").first()

        # Without token → 403
        res = c.get(f"/doctor/patient/{patient.id}/history")
        print(f"Test 4a - History without token: status={res.status_code} (expected 403)")
        assert res.status_code == 403

    # ── Test 5: add_checkup then delete within window ─────────────────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "doctor_demo", "password": "password123"})

        with app.app_context():
            patient = Patient.query.filter_by(card_id="SS-TEST-001").first()
            from app.models.user import User
            doctor = User.query.filter_by(username="doctor_demo").first()

            # Manually inject valid session token
            gen = generate_and_send_otp(patient.id, doctor.id, "+919876543210")
            entry = otp_service._otp_store.get((patient.id, doctor.id))
            for code in range(1_000_000):
                if hashlib.sha256(f"{code:06d}".encode()).hexdigest() == entry["code_hash"]:
                    correct_code = f"{code:06d}"
                    break
            tok = verify_otp(patient.id, doctor.id, correct_code)

        with c.session_transaction() as sess:
            sess["patient_access_token"] = tok
            sess["access_patient_id"] = patient.id

        # GET history
        res_hist = c.get(f"/doctor/patient/{patient.id}/history")
        print(f"Test 5a - History with valid token: status={res_hist.status_code} (expected 200)")
        assert res_hist.status_code == 200

        # POST add checkup
        res_add = c.post(f"/doctor/patient/{patient.id}/add-checkup", data={
            "area": "Ward B", "condition": "Cold",
            "medicine": "Cetirizine", "dosage": "10mg OD",
        }, follow_redirects=False)
        print(f"Test 5b - Add checkup: status={res_add.status_code} (expected 302)")
        assert res_add.status_code == 302

        # Verify new visit exists
        with app.app_context():
            new_visit = Visit.query.filter_by(condition="Cold").first()
            assert new_visit is not None
            visit_id = new_visit.id
            print(f"Test 5c - New visit in DB: id={visit_id}")

        # Delete within window (same doctor, recent)
        res_del = c.post(f"/doctor/visit/{visit_id}/delete", follow_redirects=False)
        print(f"Test 5d - Delete within window: status={res_del.status_code} (expected 302)")
        assert res_del.status_code == 302

        # Verify it's gone
        with app.app_context():
            gone = Visit.query.get(visit_id)
            assert gone is None
            print("Test 5e - Visit deleted from DB: confirmed")

    # ── Test 6: delete past window → 403 ─────────────────────────────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "doctor_demo", "password": "password123"})

        with app.app_context():
            patient = Patient.query.filter_by(card_id="SS-TEST-001").first()
            doctor = User.query.filter_by(username="doctor_demo").first()
            # Old visit (beyond edit window)
            old_visit = Visit.query.filter(
                Visit.patient_id == patient.id,
                Visit.created_at < (datetime.utcnow() - timedelta(hours=24))
            ).first()
            old_visit_id = old_visit.id

            tok2 = None
            gen2 = generate_and_send_otp(patient.id, doctor.id, "+919876543210")
            entry2 = otp_service._otp_store.get((patient.id, doctor.id))
            for code in range(1_000_000):
                if hashlib.sha256(f"{code:06d}".encode()).hexdigest() == entry2["code_hash"]:
                    tok2 = verify_otp(patient.id, doctor.id, f"{code:06d}")
                    break

        with c.session_transaction() as sess:
            sess["patient_access_token"] = tok2
            sess["access_patient_id"] = patient.id

        res_old_del = c.post(f"/doctor/visit/{old_visit_id}/delete", follow_redirects=False)
        print(f"Test 6 - Delete past window: status={res_old_del.status_code} (expected 403)")
        assert res_old_del.status_code == 403

    print("\n>>> ALL STEP 7 DOCTOR FLOW TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    run_tests()
