from datetime import datetime
from app.extensions import db


class Visit(db.Model):
    """
    Clinical checkup / visit record created by a doctor for a patient.
    created_at is an immutable timestamp used to enforce the 24h edit/delete window.
    """
    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    area = db.Column(db.String(120), nullable=False, index=True)
    condition = db.Column(db.String(255), nullable=False, index=True)
    diagnosis_notes = db.Column(db.Text, nullable=True)
    medicine = db.Column(db.String(500), nullable=False)
    dosage = db.Column(db.String(255), nullable=False)
    refill_restricted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship to doctor (User)
    doctor = db.relationship("User", foreign_keys=[created_by], backref="visits_created")

    def __repr__(self) -> str:
        return f"<Visit id={self.id} patient_id={self.patient_id} condition='{self.condition}'>"
