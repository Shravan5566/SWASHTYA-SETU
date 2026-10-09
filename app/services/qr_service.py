# pyrefly: ignore [missing-import]
"""
services/qr_service.py — Patient QR Card Generator & Card Management

Per Implementation Plan Step 7 & Step 11:
- lookup_patient_by_card: Scanned card lookup (Doctor & Pharmacist flows).
- generate_card_id: Cryptographically non-guessable, unique identifier.
- generate_qr_code: Renders QR image as a base64 data URI for instant rendering & printing.
- issue_patient_card: Registers patient, encrypts PII, issues new card (Sysadmin only).
- Strict separation: Sysadmin issues that a card exists; never manages or touches clinical visits.
"""

import base64
import io
import secrets
from typing import Dict, List, Optional, Tuple
import qrcode
from app.extensions import db
from app.models.patient import Patient
from app.utils.crypto import encrypt, decrypt


def lookup_patient_by_card(card_id: str) -> Optional[Patient]:
    """
    Given a scanned card_id string, return the matching Patient row or None.
    Used by doctor and pharmacist scan workflows.
    """
    if not card_id or not card_id.strip():
        return None
    return Patient.query.filter_by(card_id=card_id.strip()).first()


def generate_card_id() -> str:
    """
    Generate a cryptographically random, non-guessable card identifier.
    Format: SS-XXXXXXXX (e.g. SS-A8F392B1). Guarantees uniqueness in database.
    """
    while True:
        token = secrets.token_hex(4).upper()
        candidate = f"SS-{token}"
        if not Patient.query.filter_by(card_id=candidate).first():
            return candidate


def generate_qr_code(card_id: str) -> str:
    """
    Render a QR code containing card_id and return a base64-encoded PNG data URI.
    Can be used directly in <img src="..."> in templates.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(card_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_img}"


def issue_patient_card(name: str, phone: str) -> Tuple[Patient, str]:
    """
    Create a new patient record with encrypted PII and issue a unique QR card.
    Returns (patient_instance, qr_code_data_uri).
    """
    name_clean = name.strip()
    phone_clean = phone.strip()

    if not name_clean:
        raise ValueError("Patient name is required.")
    if not phone_clean:
        raise ValueError("Patient phone number is required.")

    card_id = generate_card_id()

    patient = Patient(
        card_id=card_id,
        name_encrypted=encrypt(name_clean),
        phone_encrypted=encrypt(phone_clean),
    )
    db.session.add(patient)
    db.session.commit()

    qr_data_uri = generate_qr_code(card_id)
    return patient, qr_data_uri


def get_all_patient_cards(limit: int = 100) -> List[Dict[str, str]]:
    """
    Return list of issued patient cards for Sysadmin management.
    Decrypts name & phone for display. Never queries visits or clinical notes.
    """
    patients = Patient.query.order_by(Patient.created_at.desc()).limit(limit).all()
    results = []
    for p in patients:
        try:
            name = decrypt(p.name_encrypted)
        except Exception:
            name = "(encrypted)"

        try:
            phone = decrypt(p.phone_encrypted)
        except Exception:
            phone = "(encrypted)"

        results.append({
            "id": p.id,
            "card_id": p.card_id,
            "name": name,
            "phone": phone,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return results
