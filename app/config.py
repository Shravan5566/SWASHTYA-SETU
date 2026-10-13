import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration loaded from environment variables."""
    # Secrets & Cryptographic Keys
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    FERNET_KEY = os.getenv("FERNET_KEY", "")

    # Production safety: DEBUG defaults to False unless explicitly enabled
    DEBUG = os.getenv("FLASK_DEBUG", os.getenv("DEBUG", "false")).lower() in ("true", "1", "yes")
    TESTING = os.getenv("TESTING", "false").lower() in ("true", "1", "yes")

    # Secure Session Cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in ("true", "1", "yes")

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

    # Brevo HTTPS Email API
    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
    BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "")

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
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        "Swasthya Setu Health Authority <no-reply@swasthyasetu.org>"
    )
    # Deployment Mode Configuration (False = Real Mode, True = Demo Mode)
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

    PLACEHOLDER_SECRETS = {
        "dev-secret-key-please-change-in-production",
        "change-me-to-a-long-random-string",
        "your_cryptographically_secure_flask_secret_key_here",
        "your_32_byte_base64_fernet_encryption_key_here",
        "your_smtp_app_password_here",
        "your_brevo_api_key_here",
        "placeholder",
    }

    @classmethod
    def validate_secrets(cls):
        """
        Validate critical environment variables on startup.
        Refuses to start if SECRET_KEY or FERNET_KEY is missing or still a placeholder.
        """
        errors = []
        secret = (cls.SECRET_KEY or "").strip()
        if not secret:
            errors.append("SECRET_KEY environment variable is missing.")
        elif secret in cls.PLACEHOLDER_SECRETS or "change-in-production" in secret:
            errors.append(f"SECRET_KEY cannot use insecure placeholder value.")

        fernet_k = (cls.FERNET_KEY or "").strip()
        if not fernet_k:
            errors.append("FERNET_KEY environment variable is missing. A dedicated 32-byte key is required.")
        elif fernet_k in cls.PLACEHOLDER_SECRETS:
            errors.append("FERNET_KEY cannot use insecure placeholder value.")

        # In production (not DEBUG and not DEMO_MODE and not TESTING), verify email credential is not placeholder
        if not cls.DEBUG and not cls.DEMO_MODE and not cls.TESTING:
            has_smtp = bool(cls.MAIL_USERNAME and cls.MAIL_PASSWORD and cls.MAIL_PASSWORD not in cls.PLACEHOLDER_SECRETS)
            has_brevo = bool(cls.BREVO_API_KEY and cls.BREVO_API_KEY not in cls.PLACEHOLDER_SECRETS)
            if not (has_smtp or has_brevo):
                errors.append("Production requires a valid email dispatcher (MAIL_PASSWORD or BREVO_API_KEY).")

        if errors:
            raise RuntimeError("CRITICAL SECURITY MISCONFIGURATION:\n - " + "\n - ".join(errors))


# Module-level convenience exports (used by run.py and terminal_logger)
DATABASE_URL = Config.DATABASE_URL
SECRET_KEY = Config.SECRET_KEY
FERNET_KEY = Config.FERNET_KEY
DEBUG = Config.DEBUG
OTP_PROVIDER_API_KEY = Config.OTP_PROVIDER_API_KEY
GEMINI_API_KEY = Config.GEMINI_API_KEY
AI_API_KEY = Config.AI_API_KEY
MIN_GROUP_SIZE = Config.MIN_GROUP_SIZE
DOCTOR_RECORD_EDIT_WINDOW_HOURS = Config.DOCTOR_RECORD_EDIT_WINDOW_HOURS
DEMO_MODE = Config.DEMO_MODE
BREVO_API_KEY = Config.BREVO_API_KEY
BREVO_SENDER_EMAIL = Config.BREVO_SENDER_EMAIL
