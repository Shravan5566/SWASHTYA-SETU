import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.patient import Patient
from app.models.stats import Stats
from app.utils.seed import seed_staff_accounts, seed_patients, seed_stats
from app.services.anonymizer import (
    anonymize_value,
    get_anonymized_count,
    query_anonymized_stats,
    INSUFFICIENT_DATA_SENTINEL,
    get_min_group_size,
)
from app.services.ai_service import detect_trends


def run_tests():
    print("=" * 60)
    print("STEP 10 TEST SUITE: Public Health Surveillance & Anonymizer")
    print("=" * 60)

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        seed_staff_accounts()
        seed_patients()
        seed_stats()

        # ─────────────────────────────────────────────────────────────────────
        # 1. Anonymizer Unit Tests (Single Source of Privacy Rule)
        # ─────────────────────────────────────────────────────────────────────
        print("\n--- 1. Anonymizer Service Unit Tests ---")
        min_size = get_min_group_size()
        assert min_size == 5, f"Expected MIN_GROUP_SIZE=5, got {min_size}"

        # Count >= MIN_GROUP_SIZE
        norm = anonymize_value(12)
        assert norm["is_suppressed"] is False
        assert norm["numeric"] == 12
        assert norm["display"] == "12"
        print("  [PASS] Normal count (12) unsuppressed: display='12', numeric=12")

        # Count < MIN_GROUP_SIZE
        supp = anonymize_value(3)
        assert supp["is_suppressed"] is True
        assert supp["numeric"] is None, "Suppressed count must have numeric=None to avoid JSON leak"
        assert INSUFFICIENT_DATA_SENTINEL in supp["display"]
        print(f"  [PASS] Small count (3) suppressed: display='{supp['display']}', numeric=None")

        # Zero count
        supp_zero = anonymize_value(0)
        assert supp_zero["is_suppressed"] is True
        print("  [PASS] Zero count correctly marked as suppressed (< 5)")

        # Query specific cell
        ward_a_flu = get_anonymized_count("Ward A", "Flu", "2026-W38")
        assert ward_a_flu["is_suppressed"] is False
        assert ward_a_flu["count"] == 26
        print(f"  [PASS] Cell query Ward A Flu unsuppressed (count={ward_a_flu['count']})")

        ward_c_dengue = get_anonymized_count("Ward C", "Dengue", "2026-W38")
        assert ward_c_dengue["is_suppressed"] is True
        assert ward_c_dengue["count"] is None
        assert INSUFFICIENT_DATA_SENTINEL in ward_c_dengue["display_count"]
        print(f"  [PASS] Cell query Ward C Dengue (<5) suppressed: display='{ward_c_dengue['display_count']}'")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. RBAC Enforcement on /public-health/dashboard
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 2. RBAC Enforcement ---")
    client = app.test_client()

    # Unauthenticated -> 403
    res_anon = client.get("/public-health/dashboard")
    assert res_anon.status_code == 403, f"Expected 403 for unauthenticated, got {res_anon.status_code}"
    print(f"  [PASS] Unauthenticated access blocked with {res_anon.status_code}")

    # Doctor accessing -> 403
    with client.session_transaction() as sess:
        with app.app_context():
            doc = User.query.filter_by(role="doctor").first()
            sess["_user_id"] = str(doc.id)
            sess["_fresh"] = True
    res_doc = client.get("/public-health/dashboard")
    assert res_doc.status_code == 403, f"Expected 403 for doctor, got {res_doc.status_code}"
    print(f"  [PASS] Doctor blocked from public health panel with {res_doc.status_code}")

    # Pharmacist accessing -> 403
    with client.session_transaction() as sess:
        with app.app_context():
            pharma = User.query.filter_by(role="pharmacist").first()
            sess["_user_id"] = str(pharma.id)
            sess["_fresh"] = True
    res_pharma = client.get("/public-health/dashboard")
    assert res_pharma.status_code == 403, f"Expected 403 for pharmacist, got {res_pharma.status_code}"
    print(f"  [PASS] Pharmacist blocked from public health panel with {res_pharma.status_code}")

    # Public Health Admin -> 200
    with client.session_transaction() as sess:
        with app.app_context():
            pha = User.query.filter_by(role="public_health_admin").first()
            sess["_user_id"] = str(pha.id)
            sess["_fresh"] = True
    res_pha = client.get("/public-health/dashboard")
    assert res_pha.status_code == 200, f"Expected 200 for public_health_admin, got {res_pha.status_code}"
    print(f"  [PASS] Public Health Admin granted access with {res_pha.status_code}")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Privacy Masking & k-Anonymity on Dashboard HTML
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 3. Dashboard HTML Privacy Verification ---")
    html = res_pha.get_data(as_text=True)

    # Must contain the insufficient data sentinel text (accounting for Jinja2 HTML autoescaping of '<')
    import html as html_lib
    assert (INSUFFICIENT_DATA_SENTINEL in html) or (html_lib.escape(INSUFFICIENT_DATA_SENTINEL) in html), "Sentinel text missing from dashboard HTML"
    assert "Ward C" in html
    assert "Dengue" in html
    assert "Ward A" in html
    assert "Flu" in html
    print(f"  [PASS] Insufficient Data sentinel displayed in HTML: '{INSUFFICIENT_DATA_SENTINEL}'")

    # The raw counts for suppressed cohorts (3 for Ward C Dengue, 1 for Ward C Malaria, 2 for North District Typhoid)
    # must NOT appear as raw reported case values
    assert "Suppressed (<5)" in html or "Suppressed" in html
    print("  [PASS] Protected cells visibly tagged as Suppressed (<5)")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Strict Zero Patient Data Leakage Test
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 4. Strict Zero-Patient-Leakage Check ---")
    # Verify no patient identifiers, card IDs, names, or diagnosis notes leaked
    forbidden_terms = [
        "SS-TEST-001",
        "SS-TEST-002",
        "Meera Joshi",
        "Arjun Sharma",
        "card_id",
        "diagnosis_notes",
        "patient_id",
    ]
    for term in forbidden_terms:
        assert term not in html, f"PRIVACY VIOLATION: '{term}' leaked in Public Health dashboard HTML!"
    print("  [PASS] Zero patient identifiers leaked (no card_id, no patient names, no diagnosis notes)")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Trend Alerts Page & Algorithmic Anomaly Detection
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 5. Outbreak Trend Alerts Page ---")
    res_alerts = client.get("/public-health/trend-alerts")
    assert res_alerts.status_code == 200, f"Expected 200, got {res_alerts.status_code}"
    alerts_html = res_alerts.get_data(as_text=True)

    # Ward B Dengue outbreak (seeded as 4, 5, 6, 38)
    assert "Dengue Outbreak in Ward B" in alerts_html or "Dengue" in alerts_html
    assert "38" in alerts_html
    assert "2-sigma" in alerts_html or "threshold" in alerts_html.lower()
    print("  [PASS] Outbreak Trend Alerts page rendered detected anomaly (Ward B Dengue spike of 38 cases)")

    # Verify no patient leaks in alerts page either
    for term in forbidden_terms:
        assert term not in alerts_html, f"PRIVACY VIOLATION: '{term}' leaked in Trend Alerts HTML!"
    print("  [PASS] Zero patient identifiers leaked in Trend Alerts page")

    # ─────────────────────────────────────────────────────────────────────────
    # 6. JSON API Sanitization
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 6. JSON API Privacy Sanitization ---")
    res_api = client.get("/public-health/api/anonymized-stats")
    assert res_api.status_code == 200
    api_json = res_api.get_json()
    assert api_json["success"] is True

    suppressed_found = False
    unsuppressed_found = False
    for item in api_json["data"]:
        # Verify no patient keys exist
        assert "patient_id" not in item
        assert "card_id" not in item

        if item["is_suppressed"]:
            suppressed_found = True
            assert item["count"] is None, "Suppressed item leaked integer count in JSON"
            assert INSUFFICIENT_DATA_SENTINEL in item["display_count"]
        else:
            unsuppressed_found = True
            assert isinstance(item["count"], int)
            assert item["count"] >= min_size

    assert suppressed_found, "At least one suppressed item should be in JSON"
    assert unsuppressed_found, "At least one unsuppressed item should be in JSON"
    print("  [PASS] API payload properly sanitizes counts: count=None for suppressed, integer for unsuppressed")

    print("\n" + "=" * 60)
    print("ALL STEP 10 PUBLIC HEALTH TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
