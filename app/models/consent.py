from datetime import datetime
from app.extensions import db


class ConsentGrant(db.Model):
    """
    Addition 1: Patient-Governed Dynamic Consent Grant.
    Allows patient or simulated authorized representative to grant record access
    to a named clinician or role for a defined scope and time period.
    Strictly enforced with instant backend revocation and time-based expiry.
    """
    __tablename__ = "consent_grants"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    role_target = db.Column(db.String(50), default="doctor", nullable=False)
    
    # Scopes: 'full_history', 'vitals_and_allergies', 'prescriptions_only'
    scope = db.Column(db.String(50), default="full_history", nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # Delegator: 'patient' or 'authorized_representative'
    granted_by = db.Column(db.String(50), default="patient", nullable=False)
    representative_name = db.Column(db.String(120), nullable=True)
    
    granted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    
    is_revoked = db.Column(db.Boolean, default=False, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=True)
    revoked_reason = db.Column(db.String(255), nullable=True)
    
    # Emergency Break-Glass Flag & Attributable Justification
    is_emergency = db.Column(db.Boolean, default=False, nullable=False, index=True)
    emergency_reason = db.Column(db.Text, nullable=True)
    emergency_doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relationships
    patient = db.relationship("Patient", foreign_keys=[patient_id], backref=db.backref("consent_grants", lazy="dynamic"))
    doctor = db.relationship("User", foreign_keys=[doctor_id])
    emergency_doctor = db.relationship("User", foreign_keys=[emergency_doctor_id])

    @property
    def is_active(self) -> bool:
        if self.is_revoked:
            return False
        return datetime.utcnow() < self.expires_at

    def to_dict(self) -> dict:
        doctor_name = self.doctor.full_name if self.doctor else f"Any authorized {self.role_target}"
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "doctor_name": doctor_name,
            "role_target": self.role_target,
            "scope": self.scope,
            "token": self.token,
            "granted_by": self.granted_by,
            "representative_name": self.representative_name,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_revoked": self.is_revoked,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoked_reason": self.revoked_reason,
            "is_emergency": self.is_emergency,
            "emergency_reason": self.emergency_reason,
            "is_active": self.is_active,
            "seconds_remaining": max(0, int((self.expires_at - datetime.utcnow()).total_seconds())) if not self.is_revoked else 0,
        }


class ConsentAuditLog(db.Model):
    """
    Addition 1: Attributable Consent and Emergency Access Audit Log.
    Records grants, reads, revocations, denied attempts, and emergency break-glass events.
    Enforces privacy: Administrator queries receive NO identifiable patient data.
    """
    __tablename__ = "consent_audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    patient_id = db.Column(db.Integer, nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    role_at_time = db.Column(db.String(50), nullable=True)
    
    # Actions: 'GRANT', 'READ', 'REVOKE', 'DENIED', 'EMERGENCY_OVERRIDE'
    action = db.Column(db.String(30), nullable=False, index=True)
    scope = db.Column(db.String(50), nullable=True)
    grant_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    result = db.Column(db.String(20), default="allowed", nullable=False) # 'allowed' or 'denied'
    ip_address = db.Column(db.String(60), nullable=True)

    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self, anonymize: bool = False) -> dict:
        import hashlib
        pseudo = f"ANON-{hashlib.sha256(str(self.patient_id).encode()).hexdigest()[:8]}" if (anonymize and self.patient_id) else None
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "patient_id": "[ANONYMIZED]" if anonymize else self.patient_id,
            "patient_pseudo_id": pseudo,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else "System / Anonymous",
            "role_at_time": self.role_at_time,
            "action": self.action,
            "scope": self.scope,
            "grant_id": self.grant_id,
            "details": self.details,
            "result": self.result,
            "ip_address": self.ip_address,
        }
