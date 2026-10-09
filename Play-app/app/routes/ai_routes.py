# pyrefly: ignore [missing-import]
"""
AI API endpoints for Swasthya Setu.

Provides:
- POST /ai/voice-parse: Parses dictated speech into structured checkup fields.
- POST /ai/correct-drug: Real-time spell check / fuzzy matching for prescribed medicines.
- GET /ai/summary/<patient_id>: Retrieves or refreshes clinical summary.
- GET /ai/trends: Evaluates aggregate stats to return outbreak / anomaly alerts.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.ai_service import (
    parse_voice_prescription,
    get_summary,
    invalidate_summary,
    detect_trends,
)
from app.services.drug_reference import correct_drug_name, check_conflicts, get_all_drug_names
from app.models.visit import Visit
from app.models.patient import Patient

ai_routes = Blueprint("ai_routes", __name__, url_prefix="/ai")


@ai_routes.route("/voice-parse", methods=["POST"])
@login_required
def voice_parse():
    """
    Parse a speech-to-text transcript into structured medical fields:
    {
        "area": "...",
        "condition": "...",
        "diagnosis_notes": "...",
        "medicine": "...",
        "dosage": "...",
        "refill_restricted": bool,
        "corrections": {...}
    }
    """
    data = request.get_json(silent=True) or {}
    transcript = data.get("transcript", "").strip()

    if not transcript:
        return jsonify({
            "success": False,
            "error": "Transcript is empty."
        }), 400

    parsed = parse_voice_prescription(transcript)

    return jsonify({
        "success": True,
        "data": parsed
    })


@ai_routes.route("/correct-drug", methods=["POST"])
@login_required
def correct_drug():
    """
    Live fuzzy spellcheck endpoint for the medicine input field.
    Input JSON: { "query": "paracetmol" }
    Output JSON: { "match": "Paracetamol", "score": 95, "is_corrected": true, ... }
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"match": None, "score": 0.0, "warnings": []})

    result = correct_drug_name(query, threshold=70.0)

    # Optional check against active medicines if provided
    current_meds = data.get("current_medicines", [])
    if result.get("match") and current_meds:
        conflicts = check_conflicts(result["match"], current_meds)
        if conflicts:
            result.setdefault("warnings", []).extend(conflicts)

    return jsonify(result)


@ai_routes.route("/drugs", methods=["GET"])
@login_required
def list_drugs():
    """Return catalog of known drug names for autocomplete."""
    return jsonify({
        "drugs": get_all_drug_names()
    })


@ai_routes.route("/summary/<int:patient_id>", methods=["GET"])
@login_required
def patient_summary(patient_id: int):
    """Fetch clinical summary for a given patient."""
    patient = Patient.query.get_or_404(patient_id)
    visits = Visit.query.filter_by(patient_id=patient.id).order_by(Visit.created_at.asc()).all()
    summary = get_summary(patient.id, visits)
    return jsonify({
        "patient_id": patient_id,
        "summary": summary
    })


@ai_routes.route("/summary/<int:patient_id>/invalidate", methods=["POST"])
@login_required
def invalidate_patient_summary(patient_id: int):
    """Force cache invalidation of summary."""
    invalidate_summary(patient_id)
    return jsonify({"success": True})


@ai_routes.route("/trends", methods=["GET"])
@login_required
def trends():
    """Epidemiological trend detector alerts."""
    alerts = detect_trends()
    return jsonify({
        "count": len(alerts),
        "alerts": alerts
    })
