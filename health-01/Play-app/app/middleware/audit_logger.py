# pyrefly: ignore [missing-import]
from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.access_log import AccessLog


def audit_logger(response):
    """
    after_request hook that writes one AccessLog row per request.
    Records: user_id (or None), role_at_time, endpoint, result ('allowed' or 'denied').
    """
    # Do not audit static files
    if request.path.startswith("/static"):
        return response

    try:
        user_id = None
        role_at_time = None

        if current_user and current_user.is_authenticated:
            user_id = getattr(current_user, "id", None)
            role_at_time = getattr(current_user, "role", None)

        # Result calculation: 200s & 300s are 'allowed', 403 (or 401) is 'denied'
        result = "denied" if response.status_code in (401, 403) else "allowed"

        endpoint = request.endpoint or request.path

        log_entry = AccessLog(
            user_id=user_id,
            role_at_time=role_at_time,
            endpoint=endpoint,
            result=result,
        )
        db.session.add(log_entry)
        db.session.commit()

        # Terminal security diagnostics
        if result == "denied":
            try:
                from app.utils.terminal_logger import log_security
                uname = getattr(current_user, "username", "Anonymous")
                log_security("ACCESS_DENIED", uname, role_at_time or "unauthenticated", endpoint, allowed=False, ip=request.remote_addr or "")
            except Exception:
                pass
    except Exception:
        # Prevent database logging issues from breaking the user request
        try:
            db.session.rollback()
        except Exception:
            pass

    return response
