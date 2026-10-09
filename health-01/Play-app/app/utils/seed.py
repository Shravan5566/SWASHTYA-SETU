# pyrefly: ignore [missing-import]
from app.extensions import db
from app.models.user import User
from app.models.patient import Patient
from app.models.visit import Visit
from app.utils.crypto import encrypt

DEFAULT_USERS = [
    {
        "username": "doctor_demo",
        "password": "password123",
        "role": "doctor",
        "full_name": "Dr. Aisha Verma",
    },
    {
        "username": "pharma_demo",
        "password": "password123",
        "role": "pharmacist",
        "full_name": "Rahul Patel",
    },
    {
        "username": "public_demo",
        "password": "password123",
        "role": "public_health_admin",
        "full_name": "Priya Nair",
    },
    {
        "username": "admin_demo",
        "password": "password123",
        "role": "sysadmin",
        "full_name": "Admin Vikram Rao",
    },
]


def seed_staff_accounts():
    """Seeds one account for each of the four staff roles if not already present."""
    created = []
    for udata in DEFAULT_USERS:
        existing = User.query.filter_by(username=udata["username"]).first()
        if not existing:
            user = User(
                username=udata["username"],
                role=udata["role"],
                full_name=udata["full_name"],
                is_active=True,
            )
            user.set_password(udata["password"])
            db.session.add(user)
            created.append(udata["username"])
        else:
            # Ensure password and role are active
            existing.role = udata["role"]
            existing.full_name = udata["full_name"]
            existing.is_active = True
            existing.set_password(udata["password"])

    db.session.commit()
    return created


DEFAULT_PATIENTS = [
    {"card_id": "SS-TEST-001", "name": "Meera Joshi",   "phone": "+919876543210"},
    {"card_id": "SS-TEST-002", "name": "Arjun Sharma",  "phone": "+919876543211"},
    {"card_id": "SS-TEST-003", "name": "Priya Sen",     "phone": "+919876543212"},
]


def seed_patients() -> list:
    """Seeds demo patients with encrypted PII and test visits across multiple areas/conditions."""
    from datetime import datetime, timedelta
    doctor = User.query.filter_by(username="doctor_demo").first()
    created = []
    for pd in DEFAULT_PATIENTS:
        existing = Patient.query.filter_by(card_id=pd["card_id"]).first()
        is_new = False
        if not existing:
            patient = Patient(
                card_id=pd["card_id"],
                name_encrypted=encrypt(pd["name"]),
                phone_encrypted=encrypt(pd["phone"]),
            )
            db.session.add(patient)
            db.session.flush()  # get patient.id before commit
            is_new = True
            created.append(pd["card_id"])
        else:
            patient = existing
            try:
                decrypt(patient.phone_encrypted)
            except Exception:
                patient.name_encrypted = encrypt(pd["name"])
                patient.phone_encrypted = encrypt(pd["phone"])

        if doctor and is_new:
            if pd["card_id"] == "SS-TEST-001":
                # Older visit (> 24 hours ago, immutable) - Pune Shivajinagar
                db.session.add(Visit(
                    patient_id=patient.id, created_by=doctor.id,
                    area="Shivajinagar (Ward A)", condition="Flu, Cold & Cough",
                    diagnosis_notes="Patient presented with seasonal viral fever, rhinorrhea, and persistent cough.",
                    medicine="Paracetamol, Cetirizine, Cough Syrup", dosage="500mg TDS, 10mg OD, 10ml TDS",
                    refill_restricted=False,
                    created_at=datetime.utcnow() - timedelta(days=10),
                ))
                # More recent visit
                db.session.add(Visit(
                    patient_id=patient.id, created_by=doctor.id,
                    area="Shivajinagar (Ward A)", condition="Hypertension & Chronic Headache",
                    diagnosis_notes="Blood pressure elevated at 145/95 mmHg on routine checkup with tension headache.",
                    medicine="Amlodipine, Telmisartan", dosage="5mg OD, 40mg OD",
                    refill_restricted=True,
                    created_at=datetime.utcnow() - timedelta(days=3),
                ))
            elif pd["card_id"] == "SS-TEST-002":
                db.session.add(Visit(
                    patient_id=patient.id, created_by=doctor.id,
                    area="Kothrud (Ward B)", condition="Viral Fever & Joint Pain",
                    diagnosis_notes="Acute febrile illness, body ache, normal platelet count.",
                    medicine="Paracetamol, Ibuprofen", dosage="650mg SOS, 400mg BD",
                    refill_restricted=False,
                    created_at=datetime.utcnow() - timedelta(days=5),
                ))
                db.session.add(Visit(
                    patient_id=patient.id, created_by=doctor.id,
                    area="Kothrud (Ward B)", condition="Type 2 Diabetes & Dyslipidemia",
                    diagnosis_notes="Fasting blood sugar 160 mg/dL, HbA1c 7.4%. Prescribed antidiabetic combination.",
                    medicine="Metformin, Atorvastatin", dosage="500mg BD, 10mg OD",
                    refill_restricted=False,
                    created_at=datetime.utcnow() - timedelta(days=2),
                ))
            elif pd["card_id"] == "SS-TEST-003":
                # Area Katraj Ward C (kept small under MIN_GROUP_SIZE)
                db.session.add(Visit(
                    patient_id=patient.id, created_by=doctor.id,
                    area="Katraj (Ward C)", condition="Dengue & Dehydration",
                    diagnosis_notes="Confirmed NS1 positive, low platelet count, IV fluids and antipyretics administered.",
                    medicine="Paracetamol, ORS Sachets", dosage="500mg SOS, 2L Daily",
                    refill_restricted=False,
                    created_at=datetime.utcnow() - timedelta(days=1),
                ))
    db.session.commit()
    return created


def seed_stats() -> int:
    """
    Seeds aggregate epidemiological records into the stats table for Main Pune regions.
    Includes:
    - Normal cohorts (count >= MIN_GROUP_SIZE) across Pune
    - Deliberately suppressed small cohorts (count < MIN_GROUP_SIZE) for privacy demo
    - Historical time series with an outbreak spike for trend detector validation
    """
    from app.models.stats import Stats

    demo_stats = [
        # Normal cohorts (>= 5) - Main Pune Localities
        {"area": "Shivajinagar (Ward A)", "condition": "Flu", "time_bucket": "2026-W38", "count": 26},
        {"area": "Shivajinagar (Ward A)", "condition": "Hypertension", "time_bucket": "2026-W38", "count": 19},
        {"area": "Shivajinagar (Ward A)", "condition": "Type 2 Diabetes", "time_bucket": "2026-W38", "count": 14},
        {"area": "Kothrud (Ward B)", "condition": "Flu", "time_bucket": "2026-W38", "count": 32},
        {"area": "Viman Nagar", "condition": "Acute Bronchitis", "time_bucket": "2026-W38", "count": 21},
        {"area": "Viman Nagar", "condition": "Hypertension", "time_bucket": "2026-W38", "count": 15},
        {"area": "Hadapsar", "condition": "Viral Fever", "time_bucket": "2026-W38", "count": 17},
        {"area": "Aundh", "condition": "Dengue", "time_bucket": "2026-W38", "count": 12},
        {"area": "Baner", "condition": "Viral Fever", "time_bucket": "2026-W38", "count": 16},
        {"area": "Swargate", "condition": "Gastroenteritis", "time_bucket": "2026-W38", "count": 14},
        {"area": "Camp", "condition": "Flu", "time_bucket": "2026-W38", "count": 18},
        {"area": "Deccan Gymkhana", "condition": "Hypertension", "time_bucket": "2026-W38", "count": 11},

        # Deliberately small cohorts (< 5) — must show "Insufficient Data" sentinel
        {"area": "Katraj (Ward C)", "condition": "Dengue", "time_bucket": "2026-W38", "count": 3},
        {"area": "Katraj (Ward C)", "condition": "Malaria", "time_bucket": "2026-W38", "count": 1},
        {"area": "Viman Nagar", "condition": "Typhoid", "time_bucket": "2026-W38", "count": 2},
        {"area": "Baner", "condition": "Chikungunya", "time_bucket": "2026-W38", "count": 2},
        {"area": "Deccan Gymkhana", "condition": "Malaria", "time_bucket": "2026-W38", "count": 1},

        # Outbreak spike time-series 1: Dengue in Kothrud (Ward B) (4, 5, 6, 38)
        {"area": "Kothrud (Ward B)", "condition": "Dengue", "time_bucket": "2026-W35", "count": 4},
        {"area": "Kothrud (Ward B)", "condition": "Dengue", "time_bucket": "2026-W36", "count": 5},
        {"area": "Kothrud (Ward B)", "condition": "Dengue", "time_bucket": "2026-W37", "count": 6},
        {"area": "Kothrud (Ward B)", "condition": "Dengue", "time_bucket": "2026-W38", "count": 38},

        # Outbreak spike time-series 2: Gastroenteritis in Hadapsar (3, 4, 5, 29)
        {"area": "Hadapsar", "condition": "Gastroenteritis", "time_bucket": "2026-W35", "count": 3},
        {"area": "Hadapsar", "condition": "Gastroenteritis", "time_bucket": "2026-W36", "count": 4},
        {"area": "Hadapsar", "condition": "Gastroenteritis", "time_bucket": "2026-W37", "count": 5},
        {"area": "Hadapsar", "condition": "Gastroenteritis", "time_bucket": "2026-W38", "count": 29},

        # Baseline time-series for Katraj Ward C Dengue (2, 3, 3) - enables live spike simulator
        {"area": "Katraj (Ward C)", "condition": "Dengue", "time_bucket": "2026-W36", "count": 2},
        {"area": "Katraj (Ward C)", "condition": "Dengue", "time_bucket": "2026-W37", "count": 3},
        {"area": "Katraj (Ward C)", "condition": "Dengue", "time_bucket": "2026-W38", "count": 3},
    ]

    count_added = 0
    for sdata in demo_stats:
        existing = Stats.query.filter_by(
            area=sdata["area"],
            condition=sdata["condition"],
            time_bucket=sdata["time_bucket"]
        ).first()
        if not existing:
            st = Stats(
                area=sdata["area"],
                condition=sdata["condition"],
                time_bucket=sdata["time_bucket"],
                count=sdata["count"],
            )
            db.session.add(st)
            count_added += 1
        else:
            existing.count = sdata["count"]

    db.session.commit()
    return count_added


def seed_database():
    """Seeds the entire database: staff accounts, patients, visits, and stats."""
    db.create_all()
    created_users = seed_staff_accounts()
    created_patients = seed_patients()
    seeded_stats_count = seed_stats()
    return {
        "users": created_users,
        "patients": created_patients,
        "stats": seeded_stats_count,
    }


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        results = seed_database()
        print(f"Database seeded successfully: {results}")


