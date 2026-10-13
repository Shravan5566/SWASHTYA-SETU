from datetime import datetime
from app.extensions import db


class Patient(db.Model):
    """
    Patient identity record.
    The card_id is encoded in the QR card.
    Personal identifiable information (name, phone) is stored in encrypted form.
    """
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name_encrypted = db.Column(db.Text, nullable=False)
    phone_encrypted = db.Column(db.Text, nullable=False)
    blood_group = db.Column(db.String(10), nullable=True)
    locality = db.Column(db.String(100), nullable=True)  # Pune locality
    allergies = db.Column(db.Text, nullable=True)        # Comma-separated known allergies
    chronic_conditions = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)            # Encrypted patient email (for OTP delivery)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to visits
    visits = db.relationship("Visit", backref="patient", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Patient id={self.id} card_id='{self.card_id}'>"
