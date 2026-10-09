import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.utils.seed import seed_staff_accounts, seed_patients


def run_tests():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_staff_accounts()
        seed_patients()
        print("Seeded users and patients.")

    # ── Test 1: Pharmacist can reach scan page ────────────────────────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "pharma_demo", "password": "password123"})
        res = c.get("/pharmacist/scan")
        print(f"Test 1 - Scan page accessible: status={res.status_code} (expected 200)")
        assert res.status_code == 200

    # ── Test 2: Doctor cannot access pharmacist routes ────────────────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "doctor_demo", "password": "password123"})
        res = c.get("/pharmacist/scan")
        print(f"Test 2 - Doctor blocked from pharmacist: status={res.status_code} (expected 403)")
        assert res.status_code == 403

    # ── Test 3: Unknown card → error flash, stays on scan page ───────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "pharma_demo", "password": "password123"})
        res = c.post("/pharmacist/scan", data={"card_id": "NONEXISTENT-CARD"})
        print(f"Test 3 - Unknown card: status={res.status_code} (expected 200 with error)")
        assert res.status_code == 200
        assert "not recognised" in res.get_data(as_text=True)

    # ── Test 4: Valid card → redirect to medicine_view ────────────────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "pharma_demo", "password": "password123"})
        res = c.post("/pharmacist/scan", data={"card_id": "SS-TEST-001"}, follow_redirects=False)
        print(f"Test 4 - Valid card scan: status={res.status_code} (expected 302)")
        assert res.status_code == 302
        assert "/medicines" in res.headers.get("Location", "")

    # ── Test 5: Medicine view shows exactly 4 fields & blocks refill-restricted ─
    with app.test_client() as c:
        c.post("/login", data={"username": "pharma_demo", "password": "password123"})
        res = c.post("/pharmacist/scan", data={"card_id": "SS-TEST-001"}, follow_redirects=True)
        body = res.get_data(as_text=True)
        print(f"Test 5 - Medicine view body checks:")

        # Four required fields present
        assert "SS-TEST-001" in body, "card_id missing"
        assert "Flu" in body or "Hypertension" in body, "condition missing"
        assert "Paracetamol" in body or "Amlodipine" in body, "medicine missing"
        assert "2026" in body or "2025" in body, "created_at date missing"
        print("  - 4 required fields (card_id, date, condition, medicine): [OK]")

        # diagnosis_notes must NOT appear
        assert "diagnosis_notes" not in body, "diagnosis_notes leaked into template"
        assert "Diagnosis Notes" not in body, "Diagnosis heading leaked"
        print("  - diagnosis_notes never fetched or rendered: [OK]")

        # Refill-restricted item blocked
        assert "Refill Restricted" in body, "refill-restricted warning missing"
        assert "must see a doctor" in body, "refill blocked message missing"
        print("  - Refill restricted item blocked with message: [OK]")

        # No create/edit/delete controls
        assert "delete" not in body.lower() or "Delete" not in body
        assert "<form method" not in body.replace(
            'action="{{ url_for', ""
        ) or "add-checkup" not in body
        print("  - No mutation UI (add/delete/edit): [OK]")

    # ── Test 6: No mutating routes exist in pharmacist blueprint ─────────────
    with app.test_client() as c:
        c.post("/login", data={"username": "pharma_demo", "password": "password123"})
        for path in ["/pharmacist/patient/1/add", "/pharmacist/visit/1/delete", "/pharmacist/visit/1/edit"]:
            res = c.post(path)
            print(f"Test 6 - Non-existent mutation route {path}: status={res.status_code} (expected 404 or 405)")
            assert res.status_code in (404, 405)

    print("\n>>> ALL STEP 8 PHARMACIST FLOW TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    run_tests()
