# pyrefly: ignore [missing-import]
from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """
    RBAC decorator that enforces role-based access control.

    Usage:
        @role_required('doctor')
        @role_required('doctor', 'pharmacist')   # multiple roles allowed

    Behaviour:
        - If the user is not authenticated → abort(403)
        - If the user's role is not in the allowed roles list → abort(403)
        - The view function body NEVER executes for unauthorised users.

    The 403 abort is picked up by the after_request audit_logger, which
    writes a 'denied' row to AccessLog, and then Flask renders errors/403.html.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
