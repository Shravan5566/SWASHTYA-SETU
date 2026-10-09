# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify, session
from flask_login import current_user, login_required
from app.middleware.role_required import role_required
from app.middleware.rate_limiter import rate_limit
from app.services.qr_service import lookup_patient_by_card
from app.services.otp_service import generate_and_send_otp, verify_otp
from app.utils.crypto import decrypt

ajax_routes = Blueprint("ajax_routes", __name__, url_prefix="/ajax")


@ajax_routes.route("/ping")
def ping():
    return jsonify({"status": "ok"})


@ajax_routes.route("/scan-card", methods=["POST"])
@role_required("doctor")
@rate_limit(max_requests=20, window_seconds=60, message="Scan rate limit reached. Please wait a minute.")
def scan_card():
    """
    AJAX: receive card_id from the QR scanner, look up the patient.
    On success, trigger OTP generation and return patient_id.
    """
    data = request.get_json(silent=True) or {}
    card_id = (data.get("card_id") or "").strip()

    if not card_id:
        return jsonify({"ok": False, "error": "card_id is required"}), 400

    patient = lookup_patient_by_card(card_id)
    if patient is None:
        return jsonify({"ok": False, "error": "Patient card not recognised"}), 404

    # Decrypt phone to send OTP
    try:
        phone_plain = decrypt(patient.phone_encrypted)
    except Exception:
        return jsonify({"ok": False, "error": "Could not read patient contact information"}), 500

    generate_and_send_otp(patient.id, current_user.id, phone_plain)

    # Store patient_id in session so OTP verify route knows which patient
    session["otp_patient_id"] = patient.id
    session["otp_patient_name"] = decrypt(patient.name_encrypted)

    return jsonify({"ok": True, "patient_id": patient.id})


@ajax_routes.route("/verify-otp", methods=["POST"])
@role_required("doctor")
@rate_limit(max_requests=5, window_seconds=60, message="Too many incorrect OTP attempts. Cooldown active for 1 minute.")
def verify_otp_route():
    """
    AJAX: receive the 6-digit code, verify it, issue an access token stored in session.
    """
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    patient_id = session.get("otp_patient_id")

    if not patient_id:
        return jsonify({"ok": False, "error": "No OTP flow in progress — scan a card first"}), 400

    if not code:
        return jsonify({"ok": False, "error": "OTP code is required"}), 400

    token = verify_otp(patient_id, current_user.id, code)
    if token is None:
        return jsonify({"ok": False, "error": "Invalid or expired OTP code"}), 401

    # Store the scoped access token in the session
    session["patient_access_token"] = token
    session["access_patient_id"] = patient_id

    return jsonify({"ok": True, "redirect": f"/doctor/patient/{patient_id}/history"})
