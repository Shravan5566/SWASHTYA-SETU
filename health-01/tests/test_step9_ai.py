import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.stats import Stats
from app.utils.seed import seed_staff_accounts, seed_patients
from app.services.drug_reference import (
    lookup_drug,
    correct_drug_name,
    check_conflicts,
    get_all_drug_names,
)
from app.services.ai_service import (
    get_summary,
    invalidate_summary,
    parse_voice_prescription,
    detect_outbreak_anomaly,
    detect_trends,
    call_gemini,
)


def run_tests():
    print("=" * 60)
    print("STEP 9 TEST SUITE: AI Service Layer & Clinical Drug Corrector")
    print("=" * 60)

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Drug Reference & Fuzzy Corrector Unit Tests
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 1. Drug Reference & Spell Corrector ---")
    all_drugs = get_all_drug_names()
    assert len(all_drugs) >= 100, f"Expected >= 100 drugs, found {len(all_drugs)}"
    print(f"  [PASS] Catalog contains {len(all_drugs)} canonical clinical medications")

    # Exact match
    paracetamol = lookup_drug("Paracetamol")
    assert paracetamol is not None, "Paracetamol not found in catalog"
    assert paracetamol["category"] == "Analgesic / Antipyretic"
    print("  [PASS] Exact match lookup succeeds for Paracetamol")

    # Obvious typos
    typos = [
        ("paracetmol", "Paracetamol"),
        ("amoxcilin", "Amoxicillin"),
        ("metforin", "Metformin"),
        ("atorvastin", "Atorvastatin"),
        ("pantaprazole", "Pantoprazole"),
    ]
    for typo, expected in typos:
        res = correct_drug_name(typo)
        assert res["match"] == expected, f"Expected {expected} for typo '{typo}', got {res['match']}"
        assert res["is_corrected"] is True, f"Expected is_corrected=True for '{typo}'"
        print(f"  [PASS] Corrected typo '{typo}' -> '{expected}' (score: {res['score']}%)")

    # Refill-restricted drugs flagged
    tramadol = correct_drug_name("Tramadol")
    assert tramadol["refill_restricted"] is True, "Tramadol should be marked refill_restricted"
    alprazolam = correct_drug_name("alprazolam")
    assert alprazolam["refill_restricted"] is True, "Alprazolam should be marked refill_restricted"
    print("  [PASS] Refill-restricted controlled substances correctly flagged")

    # Interaction / conflict detection
    conflicts = check_conflicts("Ibuprofen", ["Aspirin", "Paracetamol"])
    assert any("Aspirin" in c for c in conflicts), "Expected conflict between Ibuprofen and Aspirin"
    print(f"  [PASS] Conflict detector identified: {conflicts[0]}")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Voice-to-Prescription Parser
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 2. Voice-to-Prescription Parser ---")
    dictation = (
        "Patient reported to Ward A with severe acute bronchitis and high fever. "
        "Prescribed amoxcilin 500mg TDS for 7 days. Advise warm fluids and bed rest."
    )
    parsed = parse_voice_prescription(dictation)
    assert parsed["area"] == "Ward A", f"Expected 'Ward A', got {parsed['area']}"
    assert parsed["condition"] == "Acute Bronchitis", f"Expected 'Acute Bronchitis', got {parsed['condition']}"
    assert parsed["medicine"] == "Amoxicillin", f"Expected 'Amoxicillin' (auto-corrected), got {parsed['medicine']}"
    assert "500mg TDS" in parsed["dosage"], f"Expected dosage 500mg TDS, got {parsed['dosage']}"
    print(f"  [PASS] Voice dictation correctly parsed into structured fields:")
    print(f"         Area: {parsed['area']} | Condition: {parsed['condition']} | Medicine: {parsed['medicine']} | Dosage: {parsed['dosage']}")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Epidemiological Outbreak Trend Detector
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 3. Epidemiological Trend Detector ---")
    # Normal series: mean ~10, std dev ~1.4
    normal_series = [10, 11, 9, 10, 12, 10, 11]
    is_spike, mean, threshold, reason = detect_outbreak_anomaly(normal_series)
    assert not is_spike, f"Normal series should not trigger spike: {reason}"
    print(f"  [PASS] Normal variation correctly ignored (latest: {normal_series[-1]}, thresh: {threshold})")

    # Outbreak spike: mean ~10, latest 35
    outbreak_series = [10, 11, 9, 10, 12, 10, 35]
    is_spike, mean, threshold, reason = detect_outbreak_anomaly(outbreak_series)
    assert is_spike, f"Outbreak series should trigger spike: {reason}"
    print(f"  [PASS] Outbreak spike detected: latest={outbreak_series[-1]} > threshold={threshold} ({reason})")

    # ─────────────────────────────────────────────────────────────────────────
    # 4. App Context, Summarizer Caching & Invalidation
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 4. Patient Clinical Summarizer & Cache Invalidation ---")
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        seed_staff_accounts()
        seed_patients()
        patients = Patient.query.all()
        assert len(patients) > 0, "Expected at least 1 patient in database"
        patient = patients[0]

        # Fetch visits
        visits = Visit.query.filter_by(patient_id=patient.id).order_by(Visit.created_at.asc()).all()
        assert len(visits) > 0, "Expected patient to have visits"

        # 1st call: generate summary
        invalidate_summary(patient.id)
        summary1 = get_summary(patient.id, visits)
        assert summary1 and len(summary1) > 20, f"Summary too short: {summary1}"
        print(f"  [PASS] Summarizer returned clinical summary ({len(summary1.split())} words):")
        print(f"         \"{summary1[:100]}...\"")

        # 2nd call: must be from cache
        summary2 = get_summary(patient.id, visits)
        assert summary1 == summary2, "Cached summary does not match"
        print("  [PASS] Summary served from in-memory cache")

        # Invalidate cache
        invalidate_summary(patient.id)
        # Verify invalidation
        from app.services.ai_service import get_cached_summary
        assert get_cached_summary(patient.id) is None, "Cache was not invalidated"
        print("  [PASS] Cache invalidated successfully")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Gemini API Call & Mock Integration
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 5. Gemini API Integration ---")
    with patch("app.services.ai_service.requests.post") as mock_post:
        # Mock successful Gemini response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Patient has recurring seasonal viral bronchitis. Prescribed Amoxicillin with good recovery noted."}
                        ]
                    }
                }
            ]
        }

        with patch("app.services.ai_service.get_gemini_api_key", return_value="test-gemini-key"):
            result = call_gemini("Test clinical prompt")
            assert result is not None and "viral bronchitis" in result
            print(f"  [PASS] Gemini REST API successfully called & parsed response: \"{result}\"")

    # ─────────────────────────────────────────────────────────────────────────
    # 6. HTTP API Endpoints (/ai/voice-parse, /ai/correct-drug, etc.)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n--- 6. HTTP Endpoints (/ai/voice-parse, /ai/correct-drug) ---")
    client = app.test_client()

    with app.app_context():
        # Authenticate as doctor
        doctor = User.query.filter_by(role="doctor").first()
        with client.session_transaction() as sess:
            sess["_user_id"] = str(doctor.id)
            sess["_fresh"] = True

        # Test POST /ai/voice-parse
        resp = client.post("/ai/voice-parse", json={
            "transcript": "Ward B patient with Malaria prescribed Paracetmol 500mg BD"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
        json_data = resp.get_json()
        assert json_data["success"] is True
        data = json_data["data"]
        assert data["medicine"] == "Paracetamol", f"Expected Paracetamol, got {data.get('medicine')}"
        assert data["condition"] == "Malaria"
        print("  [PASS] POST /ai/voice-parse returned 200 with corrected formulary medicine")

        # Test POST /ai/correct-drug
        resp2 = client.post("/ai/correct-drug", json={"query": "metforin"})
        assert resp2.status_code == 200
        drug_res = resp2.get_json()
        assert drug_res["match"] == "Metformin"
        assert drug_res["is_corrected"] is True
        print(f"  [PASS] POST /ai/correct-drug returned 200 with suggestion '{drug_res['match']}'")

        # Test GET /ai/drugs
        resp3 = client.get("/ai/drugs")
        assert resp3.status_code == 200
        catalog = resp3.get_json()
        assert "Paracetamol" in catalog["drugs"]
        print(f"  [PASS] GET /ai/drugs returned {len(catalog['drugs'])} formulary medications")

    print("\n" + "=" * 60)
    print("ALL STEP 9 AI TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
