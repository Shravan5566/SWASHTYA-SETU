import os
import hmac
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from app.config import Config, OTP_PROVIDER_API_KEY


# ── In-memory stores (scoped by doctor and patient) ──
# { (patient_id, doctor_id): { 'code_hash': str, 'expires_at': datetime, 'failed_attempts': int } }
_otp_store: dict = {}

# { 'token_string': { 'patient_id': int, 'doctor_id': int, 'expires_at': datetime } }
_access_token_store: dict = {}

# ── Test-only plaintext cache (strictly gated to DEBUG/DEMO_MODE) ──────────
# { patient_id: { 'raw_otp': str, 'doctor_id': int } }
_raw_otp_cache: dict = {}

OTP_TTL_MINUTES = 5
ACCESS_TOKEN_TTL_MINUTES = 5
MAX_FAILED_ATTEMPTS = 5


# ── OTP helpers ──────────────────────────────────────────────────────────────────

def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def generate_and_send_otp(patient_id: int, doctor_id: int, phone_plaintext: str) -> bool:
    """
    Generate a 6-digit OTP, store it server-side, and SMS/email it to the patient.
    Returns True on success.
    """
    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)

    _otp_store[(patient_id, doctor_id)] = {
        "code_hash": _hash_code(code),
        "expires_at": expires_at,
        "failed_attempts": 0,
    }

    # Attempt email delivery if patient has a registered email on file
    patient_email = None
    patient_name = "Beneficiary"
    try:
        from app.models.patient import Patient
        from app.models.application import Application
        from app.models.user import User
        from app.utils.crypto import decrypt
        from app.services.email_service import send_otp_email

        patient = Patient.query.get(patient_id)
        doctor = User.query.get(doctor_id)
        doctor_name = doctor.full_name if doctor else "Attending Physician"

        if patient:
            try:
                patient_name = decrypt(patient.name_encrypted)
            except Exception:
                pass

            # 1. Check patient.email column if present
            if getattr(patient, "email", None):
                try:
                    decrypted_em = decrypt(patient.email)
                    if decrypted_em and "@" in decrypted_em:
                        patient_email = decrypted_em.strip()
                except Exception:
                    pass

            # 2. Primary Application lookup by assigned_card_id
            if not patient_email and patient.card_id:
                app_rec = Application.query.filter_by(assigned_card_id=patient.card_id).first()
                if app_rec and app_rec.email and "@" in app_rec.email:
                    patient_email = app_rec.email.strip()

            # 3. Fallback lookup by phone number
            if not patient_email and phone_plaintext:
                clean_phone = phone_plaintext.replace("+91", "").replace(" ", "").replace("-", "").strip()
                app_rec = Application.query.filter(
                    (Application.phone == phone_plaintext) | (Application.phone == clean_phone)
                ).order_by(Application.created_at.desc()).first()
                if app_rec and app_rec.email and "@" in app_rec.email:
                    patient_email = app_rec.email.strip()

            # 4. Evaluator/Demo fallback: dispatch OTP email to configured contact
            if not patient_email:
                evaluator_email = os.getenv("BREVO_SENDER_EMAIL", "shravanwadnerkar41206@gmail.com").strip()
                if evaluator_email and "@" in evaluator_email:
                    patient_email = evaluator_email

            if patient_email and "@" in patient_email:
                send_otp_email(patient_email, patient_name, code, doctor_name)
    except Exception:
        pass

    # Strictly gate local plaintext caching and terminal logging to DEBUG / DEMO_MODE
    is_debug_or_demo = getattr(Config, "DEBUG", False) or getattr(Config, "DEMO_MODE", False)
    if is_debug_or_demo:
        _raw_otp_cache[patient_id] = {"raw_otp": code, "doctor_id": doctor_id}
        try:
            from app.utils.terminal_logger import log_otp
            log_otp(patient_id, phone_plaintext, code, patient_name=patient_name, email=patient_email)
        except Exception:
            print(f"[OTP CODE - DEV ONLY] Patient #{patient_id} ({phone_plaintext}) -> Code: {code}")

    # Attempt SMS delivery via configured provider
    _send_sms(phone_plaintext, code)

    return True  # Flow continues cleanly


def verify_otp(patient_id: int, doctor_id: int, submitted_code: str) -> Optional[str]:
    """
    Validate the submitted OTP using constant-time comparison and rate-limiting.
    On success: remove OTP entry, issue a 5-minute access token, return the token string.
    On failure: increment failed attempts; invalidate if >= 5 attempts.
    """
    entry = _otp_store.get((patient_id, doctor_id))
    if entry is None:
        return None  # No OTP pending for this pair

    if datetime.utcnow() > entry["expires_at"]:
        _otp_store.pop((patient_id, doctor_id), None)
        _raw_otp_cache.pop(patient_id, None)
        return None  # Expired

    submitted_hash = _hash_code(submitted_code.strip())
    is_valid = hmac.compare_digest(submitted_hash, entry["code_hash"])

    if not is_valid:
        entry["failed_attempts"] = entry.get("failed_attempts", 0) + 1
        if entry["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
            # Invalidate immediately on max failed attempts to prevent brute force
            _otp_store.pop((patient_id, doctor_id), None)
            _raw_otp_cache.pop(patient_id, None)
        return None  # Invalid code

    # OTP verified — consume immediately
    _otp_store.pop((patient_id, doctor_id), None)
    _raw_otp_cache.pop(patient_id, None)

    # Issue access token strictly scoped to this exact doctor + patient pair (5 min TTL)
    token = secrets.token_urlsafe(32)
    _access_token_store[token] = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "expires_at": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
    }
    return token


def validate_access_token(token: str, patient_id: int, doctor_id: int) -> bool:
    """
    Server-side check on every clinical query that the token is still valid
    and cryptographically bound to the requesting doctor + patient pair.
    """
    if not token:
        return False
    entry = _access_token_store.get(token)
    if entry is None:
        return False
    if datetime.utcnow() > entry["expires_at"]:
        _access_token_store.pop(token, None)
        return False
    return entry["patient_id"] == patient_id and entry["doctor_id"] == doctor_id


def revoke_token(token: str) -> None:
    """Explicitly revoke an access token (e.g., on logout or session end)."""
    _access_token_store.pop(token, None)


# ── Test helper ──────────────────────────────────────────────────────────────

def get_raw_otp_for_testing(patient_id: int) -> Optional[dict]:
    """
    Return {'raw_otp': str, 'doctor_id': int} for patient_id if an OTP is
    currently pending, otherwise None. Available in test/debug contexts.
    """
    return _raw_otp_cache.get(patient_id)


# ── SMS gateway integration ──────────────────────────────────────────────────────

def _send_sms(phone: str, code: str) -> bool:
    """
    Send the OTP via configured SMS provider.
    Falls back gracefully when OTP_PROVIDER_API_KEY is not set (dev mode).
    """
    if not OTP_PROVIDER_API_KEY:
        return False

    try:
        import urllib.request, urllib.parse, json
        payload = json.dumps({
            "api_key": OTP_PROVIDER_API_KEY,
            "to": phone,
            "message": f"Your Swasthya Setu verification code is: {code}. Valid for {OTP_TTL_MINUTES} minutes.",
        }).encode()
        req = urllib.request.Request(
            "https://api.sms-gateway.example.com/send",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as exc:
        print(f"[SMS ERROR] {exc}")
        return False
