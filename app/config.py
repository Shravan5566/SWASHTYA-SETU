import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration loaded from environment variables."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-please-change-in-production")
    
    # Database URL with postgres:// -> postgresql:// fix for SQLAlchemy compatibility
    _raw_db_url = os.getenv("DATABASE_URL", "sqlite:///swasthya_setu.db")
    if _raw_db_url and _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
    
    DATABASE_URL = _raw_db_url
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Service & Integration API Keys
    OTP_PROVIDER_API_KEY = os.getenv("OTP_PROVIDER_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("AI_API_KEY", ""))
    AI_API_KEY = GEMINI_API_KEY

    # Business Rules Configuration
    MIN_GROUP_SIZE = int(os.getenv("MIN_GROUP_SIZE", 5))
    DOCTOR_RECORD_EDIT_WINDOW_HOURS = int(os.getenv("DOCTOR_RECORD_EDIT_WINDOW_HOURS", 24))

    # Email Service Configuration (Gmail SMTP)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() in ("true", "1", "yes")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "Swasthya Setu Health Authority <no-reply@swasthyasetu.org>")


# Module-level convenience exports
DATABASE_URL = Config.DATABASE_URL
SECRET_KEY = Config.SECRET_KEY
OTP_PROVIDER_API_KEY = Config.OTP_PROVIDER_API_KEY
GEMINI_API_KEY = Config.GEMINI_API_KEY
AI_API_KEY = Config.AI_API_KEY
MIN_GROUP_SIZE = Config.MIN_GROUP_SIZE
DOCTOR_RECORD_EDIT_WINDOW_HOURS = Config.DOCTOR_RECORD_EDIT_WINDOW_HOURS

