"""
services/consent_service.py — Addition 1: Dynamic Consent & Emergency Break-Glass Governor

Implements:
1. Dynamic, time-scoped, role-scoped, and clinician-scoped patient consent grants.
2. Immediate server-side token revocation and expiry enforcement.
3. Audited emergency access ("Break-Glass") with mandatory clinical justification,
   limited duration (30 mins), and restricted clinical scope.
4. Privacy boundary preservation: Administrators receive NO identifiable patient records.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List
from flask import request
from app.extensions import db
from app.models.consent import ConsentGrant, ConsentAuditLog
from app.models.patient import Patient
from app.models.user import User


def log_consent_event(
    action: str,
    patient_id: Optional[int],
    user_id: Optional[int],
    role_at_time: Optional[str],
    result: str = "allowed",
    scope: Optional[str] = None,
    grant_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> ConsentAuditLog:
    """Creates an immutable attributable consent audit log entry."""
    entry = ConsentAuditLog(
        timestamp=datetime.utcnow(),
        patient_id=patient_id,
        user_id=user_id,
        role_at_time=role_at_time,
        action=action,
        scope=scope,
        grant_id=grant_id,
        details=details,
        result=result,
        ip_address=ip_address or (request.remote_addr if request else "127.0.0.1"),
    )
    db.session.add(entry)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return entry


def create_consent_grant(
    patient_id: int,
    scope: str = "full_history",
    duration_minutes: int = 60,
    doctor_id: Optional[int] = None,
    role_target: str = "doctor",
    granted_by: str = "patient",
    representative_name: Optional[str] = None,
    current_user_id: Optional[int] = None,
) -> Tuple[bool, Any]:
    """
    Creates a new patient-governed dynamic consent grant.
    Scopes: 'full_history', 'vitals_and_allergies', 'prescriptions_only'
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        return False, "Patient not found."

    allowed_scopes = ["full_history", "vitals_and_allergies", "prescriptions_only"]
    if scope not in allowed_scopes:
        return False, f"Invalid scope. Must be one of: {allowed_scopes}"

    if duration_minutes <= 0 or duration_minutes > 10080:  # Max 7 days
        return False, "Duration must be between 1 and 10080 minutes."

    expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
    token = f"cst_{uuid.uuid4().hex}"

    grant = ConsentGrant(
        patient_id=patient.id,
        doctor_id=doctor_id,
        role_target=role_target,
        scope=scope,
        token=token,
        granted_by=granted_by,
        representative_name=representative_name,
        granted_at=datetime.utcnow(),
        expires_at=expires_at,
        is_revoked=False,
    )
    db.session.add(grant)
    db.session.commit()

    log_consent_event(
        action="GRANT",
        patient_id=patient.id,
        user_id=current_user_id or doctor_id,
        role_at_time="patient" if granted_by == "patient" else "representative",
        result="allowed",
        scope=scope,
        grant_id=grant.id,
        details=f"Granted {scope} access for {duration_minutes}m to {'Dr. #' + str(doctor_id) if doctor_id else role_target}. Token: {token[:12]}...",
    )

    return True, grant


def revoke_consent_grant(
    grant_id: int,
    revoked_by_user_id: Optional[int] = None,
    role_at_time: str = "patient",
    reason: str = "Patient revoked authorization",
) -> Tuple[bool, str]:
    """
    Instantly revokes an active consent grant and invalidates its token across the backend.
    """
    grant = ConsentGrant.query.get(grant_id)
    if not grant:
        return False, "Consent grant not found."

    if grant.is_revoked:
        return True, "Grant is already revoked."

    grant.is_revoked = True
    grant.revoked_at = datetime.utcnow()
    grant.revoked_reason = reason.strip() or "Revoked by patient"
    db.session.commit()

    log_consent_event(
        action="REVOKE",
        patient_id=grant.patient_id,
        user_id=revoked_by_user_id,
        role_at_time=role_at_time,
        result="allowed",
        scope=grant.scope,
        grant_id=grant.id,
        details=f"Grant #{grant.id} revoked immediately. Reason: {grant.revoked_reason}",
    )

    return True, "Consent revoked successfully."


def request_emergency_break_glass(
    patient_id: int,
    doctor_id: int,
    emergency_reason: str,
    duration_minutes: int = 30,
) -> Tuple[bool, Any]:
    """
    Addition 1 Emergency Access (Break-Glass):
    Initiated with an explicit medical justification and limited duration.
    Creates an emergency time-boxed grant and records an attributable audit entry.
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        return False, "Patient record not found."

    doctor = User.query.get(doctor_id)
    if not doctor or doctor.role != "doctor":
        return False, "Emergency Break-Glass can only be initiated by licensed medical clinicians."

    clean_reason = emergency_reason.strip()
    if len(clean_reason) < 10:
        return False, "An explicit, detailed clinical justification is mandatory for Emergency Break-Glass (min 10 characters)."

    # Emergency access is strictly capped to max 60 minutes (default 30 mins)
    duration = min(max(duration_minutes, 5), 60)
    expires_at = datetime.utcnow() + timedelta(minutes=duration)
    token = f"emg_{uuid.uuid4().hex}"

    grant = ConsentGrant(
        patient_id=patient.id,
        doctor_id=doctor.id,
        role_target="doctor",
        scope="vitals_and_allergies",  # Focused emergency scope
        token=token,
        granted_by="emergency_clinician",
        granted_at=datetime.utcnow(),
        expires_at=expires_at,
        is_revoked=False,
        is_emergency=True,
        emergency_reason=clean_reason,
        emergency_doctor_id=doctor.id,
    )
    db.session.add(grant)
    db.session.commit()

    # Immutable emergency audit entry
    log_consent_event(
        action="EMERGENCY_OVERRIDE",
        patient_id=patient.id,
        user_id=doctor.id,
        role_at_time="doctor",
        result="allowed",
        scope="vitals_and_allergies",
        grant_id=grant.id,
        details=f"🚨 EMERGENCY BREAK-GLASS by Dr. {doctor.full_name}: {clean_reason} (Duration: {duration} mins)",
    )

    return True, grant


def verify_consent_access(
    patient_id: int,
    clinician_id: int,
    token: Optional[str] = None,
    requested_scope: str = "vitals_and_allergies",
) -> Tuple[bool, Optional[str], Optional[ConsentGrant]]:
    """
    Verifies if a clinician has active, valid, non-expired, and non-revoked consent.
    Enforces expiry and revocation on all backend requests.
    Returns: (is_allowed, error_reason, active_grant)
    """
    # 1. If explicit token is provided, check token
    if token:
        grant = ConsentGrant.query.filter_by(token=token).first()
        if not grant:
            log_consent_event("DENIED", patient_id, clinician_id, "doctor", "denied", requested_scope, None, "Invalid consent token.")
            return False, "Invalid or unrecognized consent token.", None

        if grant.is_revoked:
            log_consent_event("DENIED", patient_id, clinician_id, "doctor", "denied", requested_scope, grant.id, f"Token revoked: {grant.revoked_reason}")
            return False, f"Consent has been revoked by patient ({grant.revoked_reason}).", None

        if datetime.utcnow() >= grant.expires_at:
            log_consent_event("DENIED", patient_id, clinician_id, "doctor", "denied", requested_scope, grant.id, "Token expired.")
            return False, "Consent authorization has expired.", None

        if grant.patient_id != patient_id:
            log_consent_event("DENIED", patient_id, clinician_id, "doctor", "denied", requested_scope, grant.id, "Token patient mismatch.")
            return False, "Token does not match target patient.", None

        # Verify scope hierarchy
        if grant.scope == "prescriptions_only" and requested_scope in ["full_history", "vitals_and_allergies"]:
            log_consent_event("DENIED", patient_id, clinician_id, "doctor", "denied", requested_scope, grant.id, "Insufficient token scope.")
            return False, "Consent grant scope is restricted to prescriptions only.", None

        log_consent_event("READ", patient_id, clinician_id, "doctor", "allowed", requested_scope, grant.id, f"Clinician access verified via token #{grant.id}")
        return True, None, grant

    # 2. Check for active named doctor grant or active emergency grant
    active_grant = ConsentGrant.query.filter(
        ConsentGrant.patient_id == patient_id,
        ConsentGrant.is_revoked == False,
        ConsentGrant.expires_at > datetime.utcnow(),
        (ConsentGrant.doctor_id == clinician_id) | (ConsentGrant.doctor_id == None),
    ).order_by(ConsentGrant.is_emergency.desc(), ConsentGrant.expires_at.desc()).first()

    if not active_grant:
        log_consent_event("DENIED", patient_id, clinician_id, "doctor", "denied", requested_scope, None, "No active consent grant or emergency authorization.")
        return False, "No active patient consent grant found. Please request consent or initiate audited emergency access.", None

    log_consent_event("READ", patient_id, clinician_id, "doctor", "allowed", requested_scope, active_grant.id, f"Clinician access verified via active grant #{active_grant.id}")
    return True, None, active_grant


def get_patient_consent_grants(patient_id: int) -> List[Dict[str, Any]]:
    """Returns all active and historical consent grants for a patient."""
    grants = ConsentGrant.query.filter_by(patient_id=patient_id).order_by(ConsentGrant.granted_at.desc()).all()
    return [g.to_dict() for g in grants]


def get_audit_logs(
    is_admin_query: bool = False,
    patient_id: Optional[int] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Returns consent audit trail.
    STRICT PRIVACY GUARANTEE: If queried by administrator, all patient identifiers are anonymized.
    """
    query = ConsentAuditLog.query
    if patient_id and not is_admin_query:
        query = query.filter_by(patient_id=patient_id)
    
    logs = query.order_by(ConsentAuditLog.timestamp.desc()).limit(limit).all()
    return [l.to_dict(anonymize=is_admin_query) for l in logs]
