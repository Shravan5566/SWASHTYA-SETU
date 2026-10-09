import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.access_log import AccessLog
from app.utils.seed import seed_staff_accounts


def run_tests():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_staff_accounts()
        print("Database initialized and seeded.")

    # --- Test 1: Unauthenticated access → 403 ---
    with app.test_client() as c:
        res = c.get("/doctor/dashboard")
        print(f"Test 1 - Unauthenticated access to /doctor/dashboard: status={res.status_code} (expected 403)")
        assert res.status_code == 403
        # Check that the 403 page body rendered
        body = res.get_data(as_text=True)
        assert "Access Denied" in body
        assert "403" in body

    # --- Test 2: Wrong role (pharmacist logging into doctor route) → 403 ---
    with app.test_client() as c:
        c.post("/login", data={"username": "pharma_demo", "password": "password123"})
        res = c.get("/doctor/dashboard")
        print(f"Test 2 - Pharmacist accessing /doctor/dashboard: status={res.status_code} (expected 403)")
        assert res.status_code == 403
        body = res.get_data(as_text=True)
        assert "Access Denied" in body

    # --- Test 3: Correct role (doctor logging into doctor route) → 200 ---
    with app.test_client() as c:
        c.post("/login", data={"username": "doctor_demo", "password": "password123"})
        res = c.get("/doctor/dashboard", follow_redirects=True)
        print(f"Test 3 - Doctor accessing /doctor/dashboard: status={res.status_code} (expected 200)")
        assert res.status_code == 200

    # --- Test 4: Audit log contains both allowed and denied rows ---
    with app.app_context():
        denied_logs = AccessLog.query.filter_by(result="denied").all()
        allowed_logs = AccessLog.query.filter_by(result="allowed").all()
        print(f"Test 4 - AccessLog: {len(denied_logs)} denied row(s), {len(allowed_logs)} allowed row(s)")
        assert len(denied_logs) >= 2, "Should have at least 2 denied rows (unauthenticated + wrong role)"
        assert len(allowed_logs) >= 1, "Should have at least 1 allowed row (correct doctor access)"

    print("\n>>> ALL STEP 6 RBAC TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    run_tests()
