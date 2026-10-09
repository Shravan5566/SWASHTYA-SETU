import os
import sys
from sqlalchemy import text
from app import create_app
from app.extensions import db
from app.config import Config
from app.utils.terminal_logger import log_startup_banner, log_db

app = create_app()

port = int(os.environ.get("PORT", 5000))
debug = os.environ.get("FLASK_ENV") == "development" or os.environ.get("DEBUG", "False").lower() in ("true", "1")

# Test and initialize database connection on startup
with app.app_context():
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    try:
        # Test connection
        db.session.execute(text("SELECT 1"))
        db.create_all()
        log_db("Database connected & verified", "All tables active (Postgres/SQLite)", success=True)
    except Exception as e:
        log_db("Database connection warning", str(e), success=False)
        print(f"\n[!] Notice: Database connection issue detected. If using Supabase pooler on port 6543, ensure SSL is active.")
        print(f"    Fallback: The application will run with available models/cache.\n")

# Print full diagnostic startup banner
log_startup_banner(
    db_uri=Config.DATABASE_URL,
    gemini_key=Config.GEMINI_API_KEY,
    mail_user=Config.MAIL_USERNAME,
    mail_server=Config.MAIL_SERVER,
    mail_port=Config.MAIL_PORT,
    server_port=port,
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=debug)

