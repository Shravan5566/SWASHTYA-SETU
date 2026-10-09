"""
Comprehensive Pune Municipal Epidemiological Dataset Seeder.
Populates realistic 6-month historical surveillance time series across Pune wards
for predictive AI trend forecasting and outbreak detection.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from app.models.stats import Stats

# Authentic Pune Ward Baseline Distributions
WARDS = [
    "Shivajinagar (Ward A)",
    "Kothrud (Ward B)",
    "Hadapsar",
    "Katraj (Ward C)",
    "Aundh",
    "Baner",
    "Viman Nagar",
    "Hinjewadi",
    "Swargate",
    "Camp",
    "Chinchwad",
    "Deccan Gymkhana",
]

# Pathogens tracked by municipal public health
CONDITIONS = [
    "Dengue",
    "Flu",
    "Viral Fever",
    "Gastroenteritis",
    "Typhoid",
    "Acute Bronchitis",
    "Malaria",
]

# Monthly multiplier progression (May -> Oct 2026)
# Reflecting real Pune monsoon dynamics (Vector spike in Aug-Oct, gastro in Jul-Aug)
MONTHS = [
    ("2026-05", "May", 0.40),
    ("2026-06", "Jun", 0.55),
    ("2026-07", "Jul", 0.75),
    ("2026-08", "Aug", 1.10),
    ("2026-09", "Sep", 1.45),
    ("2026-10", "Oct", 1.80),
]

# Baseline monthly case counts per disease in typical high-density ward
BASE_COUNTS = {
    "Dengue": 18,
    "Flu": 35,
    "Viral Fever": 28,
    "Gastroenteritis": 22,
    "Typhoid": 12,
    "Acute Bronchitis": 16,
    "Malaria": 6,
}

# Specific Ward Multipliers (Kothrud & Hadapsar have outbreak spikes)
WARD_MULTIPLIER = {
    "Kothrud (Ward B)": {"Dengue": 2.8, "Flu": 1.4},
    "Hadapsar": {"Gastroenteritis": 2.5, "Viral Fever": 1.3},
    "Shivajinagar (Ward A)": {"Flu": 1.6, "Acute Bronchitis": 1.4},
    "Katraj (Ward C)": {"Dengue": 1.2, "Malaria": 1.5},
    "Aundh": {"Dengue": 1.5, "Flu": 1.1},
    "Viman Nagar": {"Acute Bronchitis": 1.8, "Typhoid": 1.3},
    "Swargate": {"Gastroenteritis": 1.7, "Typhoid": 1.4},
    "Camp": {"Flu": 1.3, "Gastroenteritis": 1.2},
    "Baner": {"Viral Fever": 1.2, "Dengue": 1.1},
    "Hinjewadi": {"Flu": 1.4, "Acute Bronchitis": 1.5},
    "Chinchwad": {"Viral Fever": 1.3, "Acute Bronchitis": 1.4},
    "Deccan Gymkhana": {"Flu": 1.0, "Dengue": 0.9},
}


def seed_epidemiological_data():
    app = create_app()
    with app.app_context():
        print("[*] Generating 6-month historical epidemiological telemetry...")
        added = 0
        updated = 0

        for bucket, month_name, time_factor in MONTHS:
            for ward in WARDS:
                ward_mults = WARD_MULTIPLIER.get(ward, {})
                for cond in CONDITIONS:
                    base = BASE_COUNTS.get(cond, 15)
                    ward_factor = ward_mults.get(cond, 1.0)

                    # Seasonal disease weighting
                    seasonal = 1.0
                    if cond in ("Dengue", "Malaria"):
                        # Monsoon vector spike in Aug-Oct
                        seasonal = 0.5 if bucket in ("2026-05", "2026-06") else (1.6 if bucket in ("2026-09", "2026-10") else 1.1)
                    elif cond in ("Gastroenteritis", "Typhoid"):
                        # Water contamination peak in Jul-Sep
                        seasonal = 0.8 if bucket in ("2026-05",) else (1.4 if bucket in ("2026-07", "2026-08") else 1.2)
                    elif cond in ("Flu", "Viral Fever", "Acute Bronchitis"):
                        seasonal = 0.9 if bucket in ("2026-05", "2026-06") else 1.3

                    calculated_count = int(round(base * time_factor * ward_factor * seasonal))
                    calculated_count = max(1, calculated_count)

                    existing = Stats.query.filter_by(
                        area=ward,
                        condition=cond,
                        time_bucket=bucket
                    ).first()

                    if not existing:
                        st = Stats(
                            area=ward,
                            condition=cond,
                            time_bucket=bucket,
                            count=calculated_count
                        )
                        db.session.add(st)
                        added += 1
                    else:
                        existing.count = calculated_count
                        updated += 1

        db.session.commit()
        total_rows = Stats.query.count()
        print(f"[OK] Seeding complete: {added} rows added, {updated} updated.")
        print(f"[*] Total Stats cohorts in database: {total_rows}")


if __name__ == "__main__":
    seed_epidemiological_data()
