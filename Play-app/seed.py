"""
CLI entrypoint to seed the database configured in .env (SQLite, Supabase, or Railway PostgreSQL).
Usage:
    python seed.py
"""
import os
import sys
from app import create_app
from app.utils.seed import seed_database

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        # Mask password in URI for clean logging
        safe_uri = db_uri
        if "@" in db_uri:
            prefix, rest = db_uri.split("@", 1)
            if ":" in prefix:
                proto_user = prefix.rsplit(":", 1)[0]
                safe_uri = f"{proto_user}:****@{rest}"
        print(f"[*] Seeding database target: {safe_uri}")
        results = seed_database()
        print("[OK] Database seeded successfully:")
        print(f"    - Staff accounts: {results.get('users')}")
        print(f"    - Patient cards: {results.get('patients')}")
        print(f"    - Stats cohorts: {results.get('stats')} rows")
