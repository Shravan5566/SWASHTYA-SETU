from datetime import datetime
import secrets
from app.extensions import db


class Application(db.Model):
    """
    Public registration applications for:
    1. Digital Health Card (Patient)
    2. Healthcare Staff (Doctor / Pharmacist)

    These applications undergo verification by System Administrators.
    Public Health Admin cannot be applied for publicly; it is created solely by SysAdmin.
    """
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    app_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    app_type = db.Column(db.String(20), nullable=False)  # 'health_card' or 'staff'
    role = db.Column(db.String(30), nullable=False)      # 'patient', 'doctor', 'pharmacist'
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)  # pending, approved, rejected

    # Personal info
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=False)
    dob = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)

    # Identification & Location
    gov_id_type = db.Column(db.String(30), nullable=True)
    gov_id_number = db.Column(db.String(50), nullable=True)
    locality = db.Column(db.String(100), nullable=True)  # Pune Locality
    address = db.Column(db.Text, nullable=True)

    # Health Card Specific
    emergency_name = db.Column(db.String(120), nullable=True)
    emergency_phone = db.Column(db.String(30), nullable=True)
    emergency_relation = db.Column(db.String(50), nullable=True)
    chronic_conditions = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)

    # Staff Specific (Doctor / Pharmacist)
    council_reg_no = db.Column(db.String(80), nullable=True)  # MMC / MSPC number
    qualification = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    experience_years = db.Column(db.String(20), nullable=True)
    workplace_name = db.Column(db.String(150), nullable=True)
    workplace_address = db.Column(db.Text, nullable=True)

    # Screening & Approval Output
    admin_notes = db.Column(db.Text, nullable=True)
    assigned_card_id = db.Column(db.String(100), nullable=True)
    assigned_username = db.Column(db.String(80), nullable=True)
    assigned_password = db.Column(db.String(80), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    @classmethod
    def generate_app_no(cls, role: str) -> str:
        prefix = {
            "doctor": "APP-DOC",
            "pharmacist": "APP-PHM",
            "patient": "APP-PAT",
        }.get(role, "APP-GEN")
        token = secrets.token_hex(3).upper()
        return f"{prefix}-{token}"

    def __repr__(self) -> str:
        return f"<Application app_no='{self.app_no}' role='{self.role}' status='{self.status}'>"
