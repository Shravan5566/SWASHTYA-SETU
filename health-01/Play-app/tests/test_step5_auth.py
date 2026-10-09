import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.utils.seed import seed_staff_accounts


def run_tests():
    app = create_app()
    with app.app_context():
        db.create_all()
        created = seed_staff_accounts()
        print("Database seeded with accounts:", created)

    client = app.test_client()

    # 1. Test wrong password
    res = client.post("/login", data={"username": "doctor_demo", "password": "wrongpassword"})
    print(f"Test 1 - Wrong password: status={res.status_code}")
    assert res.status_code == 401
    assert "Invalid username or password" in res.get_data(as_text=True)

    # 2. Test nonexistent user
    res = client.post("/login", data={"username": "unknown_user", "password": "randompassword"})
    print(f"Test 2 - Unknown user: status={res.status_code}")
    assert res.status_code == 401

    # 3. Test all 4 staff roles: login and redirection
    role_tests = [
        ("doctor_demo", "password123", "/doctor/dashboard"),
        ("pharma_demo", "password123", "/pharmacist/scan"),
        ("public_demo", "password123", "/public-health/dashboard"),
        ("admin_demo", "password123", "/admin/dashboard"),
    ]

    for username, password, expected_path in role_tests:
        with app.test_client() as c:
            res = c.post("/login", data={"username": username, "password": password}, follow_redirects=False)
            loc = res.headers.get("Location")
            print(f"Test 3 - Role [{username}]: status={res.status_code}, redirect='{loc}' (expected='{expected_path}')")
            assert res.status_code == 302
            assert loc == expected_path
            
            # Follow redirect to dashboard
            res_dash = c.get(expected_path, follow_redirects=True)
            assert res_dash.status_code == 200

    # 4. Test logout
    with app.test_client() as c:
        c.post("/login", data={"username": "doctor_demo", "password": "password123"})
        res_logout = c.get("/logout", follow_redirects=False)
        loc = res_logout.headers.get("Location")
        print(f"Test 4 - Logout: status={res_logout.status_code}, redirect='{loc}'")
        assert res_logout.status_code == 302
        assert loc == "/login"

    # 5. Confirm no public self-registration routes exist
    res_reg = client.get("/register")
    assert res_reg.status_code == 404
    print("Test 5 - No self-registration route (404 as required): confirmed.")

    print("\n>>> ALL STEP 5 AUTH TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    run_tests()
