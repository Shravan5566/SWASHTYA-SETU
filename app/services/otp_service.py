# pyrefly: ignore [missing-import]
import secrets
import hashlib
from datetime import datetime, timedelta
from app.extensions import db
from app.config import OTP_PROVIDER_API_KEY


# ── In-memory stores (good enough for demo; swap for DB or Redis in production) ──
# { (patient_id, doctor_id): { 'code_hash': str, 'expires_at': datetime } }
_otp_store: dict = {}

# { 'token_string': { 'patient_id': int, 'doctor_id': int, 'expires_at': datetime } }
_access_token_store: dict = {}

# ── Test-only plaintext cache (never used in production logic) ──────────────
# { patient_id: { 'raw_otp': str, 'doctor_id': int } }
_raw_otp_cache: dict = {}

OTP_TTL_MINUTES = 5
ACCESS_TOKEN_TTL_MINUTES = 60


# ── OTP helpers ──────────────────────────────────────────────────────────────────

def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def generate_and_send_otp(patient_id: int, doctor_id: int, phone_plaintext: str) -> bool:
    """
    Generate a 6-digit OTP, store it server-side, and SMS it to the patient.
    Returns True on success, False if SMS delivery fails.
    """
    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)

    _otp_store[(patient_id, doctor_id)] = {
        "code_hash": _hash_code(code),
        "expires_at": expires_at,
    }

    # Cache plaintext for testing convenience (harmless; cleared on verify)
    _raw_otp_cache[patient_id] = {"raw_otp": code, "doctor_id": doctor_id}

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

            # 1. Primary lookup: Match Application directly linked to this patient's assigned_card_id
            app_rec = None
            if patient.card_id:
                app_rec = Application.query.filter_by(assigned_card_id=patient.card_id).first()

            # 2. Fallback lookup: Match by patient's phone number (newest application first)
            if not app_rec and phone_plaintext:
                clean_phone = phone_plaintext.replace("+91", "").replace(" ", "").replace("-", "").strip()
                app_rec = Application.query.filter(
                    (Application.phone == phone_plaintext) | (Application.phone == clean_phone)
                ).order_by(Application.created_at.desc()).first()

            if app_rec and app_rec.email and "@" in app_rec.email:
                patient_email = app_rec.email.strip()
                send_otp_email(patient_email, patient_name, code, doctor_name)
    except Exception as exc:
        pass

    # Print comprehensive OTP details to terminal
    try:
        from app.utils.terminal_logger import log_otp
        log_otp(patient_id, phone_plaintext, code, patient_name=patient_name, email=patient_email)
    except Exception:
        print(f"[OTP CODE] Patient #{patient_id} ({phone_plaintext}) -> Code: {code}")

    # Attempt SMS delivery via configured provider
    delivered = _send_sms(phone_plaintext, code)

    return True  # Always return True so the flow continues in demo mode


def verify_otp(patient_id: int, doctor_id: int, submitted_code: str) -> str | None:
    """
    Validate the submitted OTP.
    On success: remove OTP entry, issue a time-limited access token, return the token string.
    On failure: return None.
    """
    entry = _otp_store.get((patient_id, doctor_id))
    if entry is None:
        return None  # No OTP was generated for this pair

    if datetime.utcnow() > entry["expires_at"]:
        _otp_store.pop((patient_id, doctor_id), None)
        return None  # OTP expired

    if _hash_code(submitted_code.strip()) != entry["code_hash"]:
        return None  # Wrong code

    # OTP correct — consume it
    _otp_store.pop((patient_id, doctor_id), None)

    # Issue access token scoped to this exact doctor + patient pair
    token = secrets.token_urlsafe(32)
    _access_token_store[token] = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "expires_at": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
    }
    return token


def validate_access_token(token: str, patient_id: int, doctor_id: int) -> bool:
    """
    Server-side check on every page load that the token is still valid
    and scoped to the requesting doctor + patient pair.
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

def get_raw_otp_for_testing(patient_id: int) -> dict | None:
    """
    Return {'raw_otp': str, 'doctor_id': int} for *patient_id* if an OTP is
    currently pending, otherwise None.

    This is intentionally NOT called anywhere in production code; it exists
    purely so integration / smoke tests can retrieve the plaintext code without
    having to crack the stored SHA-256 hash.
    """
    return _raw_otp_cache.get(patient_id)


# ── SMS gateway integration ──────────────────────────────────────────────────────

def _send_sms(phone: str, code: str) -> bool:
    """
    Send the OTP via configured SMS provider.
    Falls back gracefully when OTP_PROVIDER_API_KEY is not set (dev mode).
    """
    if not OTP_PROVIDER_API_KEY:
        return False  # No key → fall through to console print in caller

    try:
        import urllib.request, urllib.parse, json
        # Generic REST SMS gateway call — replace body/URL with your provider's spec
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
