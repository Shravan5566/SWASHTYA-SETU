"""
tests/test_security_compliance.py — Comprehensive Security & Compliance Test Suite
Validates:
(a) Strict server-side RBAC enforcement (401/403) for unauthenticated requests.
(b) Clinical record privacy barrier (OTP required; cannot view records without active OTP session token).
(c) Public health privacy suppression (k-anonymity k >= 5 distinct patients; suppressed cells return None).
(d) App refuses to start when critical secrets are missing or placeholders.
(e) OTP hardening: 5-attempt brute-force limit immediately invalidates OTP.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.config import Config
from app.extensions import db
from app.models.user import User
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.stats import Stats
from app.services.otp_service import (
    generate_and_send_otp,
    verify_otp,
    _otp_store,
    _access_token_store,
)
from app.utils.crypto import encrypt, decrypt


class TestSecurityConfig(Config):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-security-secret-key-at-least-32-chars-long"
    FERNET_KEY = "HObXoEYFeACbBVRePHgSthsWJUFAGckNyyp0GYjc43w="


class SecurityComplianceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestSecurityConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        # Create test users with mandatory full_name
        admin_user = User(username="sec_admin", full_name="Security Admin", role="admin")
        admin_user.set_password("Admin@123")
        doc_user = User(username="sec_doc", full_name="Dr. Security Doc", role="doctor")
        doc_user.set_password("Doc@123")
        pharm_user = User(username="sec_pharm", full_name="Security Pharmacist", role="pharmacist")
        pharm_user.set_password("Pharm@123")
        health_user = User(username="sec_health", full_name="Security Epidemiologist", role="public_health")
        health_user.set_password("Health@123")

        db.session.add_all([admin_user, doc_user, pharm_user, health_user])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        _otp_store.clear()
        _access_token_store.clear()

    # ── Test Suite 1: RBAC Enforcement ──────────────────────────────────────────

    def test_unauthenticated_cannot_access_protected_endpoints(self):
        """(a) Prove unauthenticated requests receive 401 or 403 on protected endpoints."""
        endpoints = [
            "/api/pharmacy/queue",
            "/api/admin/queue",
            "/api/surveillance",
            "/api/patients/SS-SEC-001/records",
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertIn(
                res.status_code,
                (401, 403),
                f"Endpoint {ep} allowed unauthenticated access (status: {res.status_code})",
            )

    def test_doctor_cannot_browse_quick_patients(self):
        """(a.2) Prove deprecated quick-patients endpoint refuses patient browsing."""
        # Login as doctor via REST API
        login_res = self.client.post("/api/auth/login", json={"username": "sec_doc", "password": "Doc@123"})
        self.assertEqual(login_res.status_code, 200)

        res = self.client.get("/api/quick-patients")
        self.assertEqual(res.status_code, 410)  # Deprecated and restricted

    # ── Test Suite 2: Doctor OTP Enforcement ─────────────────────────────────────

    def test_doctor_cannot_view_records_without_otp_session(self):
        """(b) Prove doctor cannot view patient clinical dossier without valid OTP token."""
        pat = Patient(
            card_id="SS-SEC-001",
            name_encrypted=encrypt("Siddhesh Sahane"),
            phone_encrypted=encrypt("9876543210"),
            blood_group="O+",
            locality="Shivajinagar",
        )
        db.session.add(pat)
        db.session.commit()

        # Doctor logs in via REST API
        login_res = self.client.post("/api/auth/login", json={"username": "sec_doc", "password": "Doc@123"})
        self.assertEqual(login_res.status_code, 200)

        # Try to view records directly without OTP access token
        res = self.client.get("/api/patients/SS-SEC-001/records")
        self.assertEqual(res.status_code, 403)
        data = res.get_json()
        self.assertIn("consent", data.get("error", "").lower())

    def test_otp_brute_force_lockout_after_5_attempts(self):
        """(b.2) Prove OTP is invalidated after 5 failed verification attempts."""
        doc = User.query.filter_by(username="sec_doc").first()
        pat = Patient(
            card_id="SS-SEC-002",
            name_encrypted=encrypt("Meera Joshi"),
            phone_encrypted=encrypt("9876543211"),
            blood_group="A+",
            locality="Kothrud",
        )
        db.session.add(pat)
        db.session.commit()

        # Generate OTP
        generate_and_send_otp(pat.id, doc.id, "9876543211")
        self.assertIn((pat.id, doc.id), _otp_store)

        # 4 failed attempts: OTP should still be active
        for _ in range(4):
            token = verify_otp(pat.id, doc.id, "000000")
            self.assertIsNone(token)
            self.assertIn((pat.id, doc.id), _otp_store)

        # 5th failed attempt: OTP must be purged from memory
        token = verify_otp(pat.id, doc.id, "000000")
        self.assertIsNone(token)
        self.assertNotIn((pat.id, doc.id), _otp_store)

    # ── Test Suite 3: Public Health K-Anonymity Suppression ─────────────────────

    def test_k_anonymity_suppression_below_5_distinct_patients(self):
        """(c) Prove cohorts with fewer than 5 distinct patients are suppressed to None."""
        small_stat = Stats(area="Kothrud", condition="Dengue", time_bucket="2026-W40", count=3)
        large_stat = Stats(area="Katraj", condition="Flu", time_bucket="2026-W40", count=14)
        db.session.add_all([small_stat, large_stat])
        db.session.commit()

        # Login as public health officer
        login_res = self.client.post("/api/auth/login", json={"username": "sec_health", "password": "Health@123"})
        self.assertEqual(login_res.status_code, 200)

        res = self.client.get("/api/surveillance")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        cells = data.get("cells", [])

        # Small stat cell (Kothrud, Dengue): count = 3 < 5
        kothrud_cell = next((c for c in cells if c["locality"] == "Kothrud" and c["disease"] == "Dengue"), None)
        self.assertIsNotNone(kothrud_cell)
        self.assertTrue(kothrud_cell["suppressed"])
        self.assertIsNone(kothrud_cell["cases"])  # Strictly None, never 0 or leaking count

        # Large stat cell (Katraj, Flu): count = 14 >= 5
        katraj_cell = next((c for c in cells if c["locality"] == "Katraj" and c["disease"] == "Flu"), None)
        self.assertIsNotNone(katraj_cell)
        self.assertFalse(katraj_cell["suppressed"])
        self.assertEqual(katraj_cell["cases"], 14)

    # ── Test Suite 4: Startup Fail-Fast Secrets Validation ───────────────────────

    def test_app_refuses_to_start_when_secret_key_is_missing(self):
        """(d.1) Prove app refuses to start without SECRET_KEY."""
        class BrokenConfig(Config):
            SECRET_KEY = ""
            FERNET_KEY = "HObXoEYFeACbBVRePHgSthsWJUFAGckNyyp0GYjc43w="

        with self.assertRaises(RuntimeError) as ctx:
            create_app(BrokenConfig)
        self.assertIn("SECRET_KEY environment variable is missing", str(ctx.exception))

    def test_app_refuses_to_start_when_fernet_key_is_missing(self):
        """(d.2) Prove app refuses to start without FERNET_KEY."""
        class BrokenConfig(Config):
            SECRET_KEY = "valid-secret-key-at-least-32-chars-long"
            FERNET_KEY = ""

        with self.assertRaises(RuntimeError) as ctx:
            create_app(BrokenConfig)
        self.assertIn("FERNET_KEY environment variable is missing", str(ctx.exception))

    def test_app_refuses_to_start_with_placeholder_secrets(self):
        """(d.3) Prove app refuses to start if placeholder secrets are supplied."""
        class BrokenConfig(Config):
            SECRET_KEY = "dev-secret-key-please-change-in-production"
            FERNET_KEY = "HObXoEYFeACbBVRePHgSthsWJUFAGckNyyp0GYjc43w="

        with self.assertRaises(RuntimeError) as ctx:
            create_app(BrokenConfig)
        self.assertIn("SECRET_KEY cannot use insecure placeholder value", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
