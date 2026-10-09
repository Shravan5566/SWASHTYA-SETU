# pyrefly: ignore [missing-import]
"""
utils/terminal_logger.py — Real-Time Terminal Activity & Diagnostics Layer

Prints real-time operational events to the server console:
- Database connectivity & initialization status
- OTP generation, codes, and dispatch to phone/email
- Email SMTP dispatch (success, retries, errors)
- AI Gemini service calls (transcription, clinical summarization)
- Security events (RBAC 403 blocks, Rate Limit 429 warnings)

Formatted with ANSI colors and fully compatible with Windows terminal / PowerShell.
"""

import sys
from datetime import datetime

# Windows terminal UTF-8 support
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log_startup_banner(db_uri: str, gemini_key: str, mail_user: str, mail_server: str, mail_port: int, server_port: int):
    """Print full system diagnostic startup card in the terminal."""
    print(f"\n{CYAN}{BOLD}" + "=" * 70)
    print("   🏥 SWASTHYA SETU — PUNE MUNICIPAL DIGITAL HEALTH PLATFORM")
    print("   Real-Time Server Console & Service Activity Logger")
    print("=" * 70 + f"{RESET}")

    # Database
    safe_db = db_uri
    if "@" in safe_db:
        prefix, rest = safe_db.split("@", 1)
        proto = prefix.split("://")[0] if "://" in prefix else "db"
        user = prefix.split("://")[-1].split(":")[0] if "://" in prefix else "user"
        safe_db = f"{proto}://{user}:****@{rest}"
    print(f"\n{BOLD}🔌 [DATABASE SUBSYSTEM]{RESET}")
    print(f"   Target URI    : {BLUE}{safe_db}{RESET}")

    # AI Gemini
    print(f"\n{BOLD}🤖 [AI & CLINICAL NLP SUBSYSTEM]{RESET}")
    if gemini_key:
        preview = f"{gemini_key[:8]}...{gemini_key[-6:]}" if len(gemini_key) > 14 else "***"
        print(f"   Google Gemini : {GREEN}ACTIVE{RESET} (Key: {preview})")
        print(f"   Models In Use : gemini-1.5-flash, gemini-2.0-flash, gemini-1.5-pro")
        print(f"   Offline Cache : In-memory differential cache enabled")
    else:
        print(f"   Google Gemini : {YELLOW}OFFLINE / FALLBACK{RESET} (Rule-based NLP engine active)")

    # Gmail SMTP
    print(f"\n{BOLD}📧 [NOTIFICATION SUBSYSTEM (GMAIL SMTP)]{RESET}")
    if mail_user:
        print(f"   Sender Account: {GREEN}{mail_user}{RESET}")
        print(f"   SMTP Server   : {mail_server}:{mail_port} (TLS Enabled)")
    else:
        print(f"   Sender Account: {YELLOW}NOT CONFIGURED{RESET} (Simulated console mode)")

    # OTP / Delivery
    print(f"\n{BOLD}📱 [OTP SUBSYSTEM]{RESET}")
    print(f"   Delivery Mode  : {CYAN}Gmail (SMTP){RESET}  — OTP sent to patient's registered email")
    print(f"   SMS Provider   : {YELLOW}NOT CONFIGURED{RESET} (Twilio key empty — using Gmail only)")
    print(f"   Terminal Print : {GREEN}ENABLED{RESET} (OTP code always visible here in real-time)")
    print(f"   Fallback       : {GREEN}ENABLED{RESET} (If no email on file, OTP shown in terminal only)")

    # Rate Limiting
    print(f"\n{BOLD}🛡️ [SECURITY & RATE LIMITING]{RESET}")
    print(f"   Rate Limiter  : {GREEN}ACTIVE{RESET} (Protects /login, /apply, /verify-otp, /admin)")
    print(f"   RBAC & Audit  : {GREEN}ACTIVE{RESET} (All access decisions logged to AccessLog table)")

    # Endpoints
    print(f"\n{GREEN}{BOLD}🚀 Server listening at: http://127.0.0.1:{server_port}{RESET}")
    print(f"{DIM}Press Ctrl+C to stop the server.{RESET}\n")
    print(f"{CYAN}{'-' * 70}{RESET}\n")


def log_db(event: str, details: str = "", success: bool = True):
    """Log database connection / query / schema event."""
    tag = f"{GREEN}[DB OK]{RESET}" if success else f"{RED}[DB ERROR]{RESET}"
    det = f" | {details}" if details else ""
    print(f"{DIM}{_timestamp()}{RESET} {tag} {event}{det}")


def log_otp(patient_id: int, phone: str, code: str, patient_name: str = "", email: str = None):
    """Log generated OTP with Gmail delivery details."""
    print(f"\n{MAGENTA}{BOLD}" + "─" * 60)
    print(f"🔐 [OTP GENERATED] Authorization Code for Patient #{patient_id}")
    print(f"   Patient Name   : {patient_name or 'Registered Beneficiary'}")
    print(f"   Phone (ref)    : {YELLOW}{phone}{RESET}  (SMS: not configured)")
    if email:
        print(f"   📧 Patient Email: {GREEN}{BOLD}{email}{RESET}  ← Dispatched to Patient's Email")
    else:
        print(f"   📧 Patient Email: {YELLOW}No email registered for this card — shown in terminal only{RESET}")
    print(f"   >>> VERIFICATION CODE: {GREEN}{BOLD}[ {code} ]{RESET} (Expires in 5 mins)")
    print(f"{MAGENTA}{BOLD}" + "─" * 60 + f"{RESET}\n")


def log_email(to_email: str, subject: str, success: bool, reason: str = ""):
    """Log email dispatch event."""
    if success:
        print(f"{DIM}{_timestamp()}{RESET} {GREEN}[EMAIL SENT]{RESET} To: {CYAN}{to_email}{RESET} | Subject: '{subject}'")
    else:
        print(f"{DIM}{_timestamp()}{RESET} {YELLOW}[EMAIL NOTICE]{RESET} To: {to_email} | Subject: '{subject}' -> ({reason})")


def log_ai(service: str, details: str, success: bool = True):
    """Log AI summarizer or voice parsing event."""
    tag = f"{CYAN}[AI {service.upper()}]{RESET}"
    status = f"{GREEN}OK{RESET}" if success else f"{YELLOW}FALLBACK{RESET}"
    print(f"{DIM}{_timestamp()}{RESET} {tag} ({status}): {details}")


def log_security(event: str, user: str, role: str, endpoint: str, allowed: bool = True, ip: str = ""):
    """Log security / RBAC / Rate limiting decision."""
    if allowed:
        tag = f"{GREEN}[RBAC ALLOWED]{RESET}"
        print(f"{DIM}{_timestamp()}{RESET} {tag} {role.upper()} '{user}' -> {endpoint}")
    else:
        tag = f"{RED}{BOLD}[RBAC DENIED 403]{RESET}"
        print(f"{DIM}{_timestamp()}{RESET} {tag} User '{user}' ({role}) BLOCKED from {endpoint} {f'(IP: {ip})' if ip else ''}")


def log_rate_limit(endpoint: str, client_id: str, retry_after: int):
    """Log rate limiting trigger."""
    print(f"{DIM}{_timestamp()}{RESET} {YELLOW}{BOLD}[RATE LIMIT 429]{RESET} Client '{client_id}' exceeded limit on {endpoint} (Cooldown: {retry_after}s)")
