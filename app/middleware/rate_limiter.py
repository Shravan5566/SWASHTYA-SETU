# pyrefly: ignore [missing-import]
"""
middleware/rate_limiter.py — In-Memory Sliding Window Rate Limiter

Protects:
1. Public submission portals (/apply/health-card, /apply/staff) against automated spamming.
2. Authentication endpoints (/login) against credential stuffing and brute force.
3. OTP endpoints (/ajax/verify-otp) against PIN enumeration attacks.
4. Staff & Administrative panels against request flooding.

Returns HTTP 429 Too Many Requests when rate limits are exceeded,
with Retry-After header and clean HTML or JSON error payload.
"""

import time
import threading
from functools import wraps
from typing import Dict, List, Optional
from flask import request, jsonify, render_template, Response, flash, redirect, url_for
from flask_login import current_user

_lock = threading.Lock()
# { key: [timestamp1, timestamp2, ...] }
_request_records: Dict[str, List[float]] = {}


def _get_client_identifier() -> str:
    """Derive unique client key using authenticated user ID or real IP address."""
    if current_user and current_user.is_authenticated:
        return f"user:{current_user.id}"
    
    # Check for reverse proxy headers (e.g. Railway, Cloudflare, Nginx)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.remote_addr or "127.0.0.1"
    
    return f"ip:{client_ip}"


def is_rate_limited(key: str, max_requests: int, window_seconds: int) -> bool:
    """
    Check and record request using sliding window algorithm.
    Returns True if rate limit is exceeded, False otherwise.
    """
    now = time.time()
    cutoff = now - window_seconds

    with _lock:
        timestamps = _request_records.setdefault(key, [])
        # Prune old timestamps outside current sliding window
        valid_timestamps = [t for t in timestamps if t > cutoff]
        _request_records[key] = valid_timestamps

        if len(valid_timestamps) >= max_requests:
            return True

        valid_timestamps.append(now)
        return False


def rate_limit(max_requests: int = 60, window_seconds: int = 60, message: Optional[str] = None):
    """
    Decorator to apply custom rate limiting to specific Flask view routes.
    
    Example:
        @auth_routes.route("/login", methods=["POST"])
        @rate_limit(max_requests=10, window_seconds=60)
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = request.endpoint or f.__name__
            client_id = _get_client_identifier()
            rate_key = f"{endpoint}:{client_id}"

            if is_rate_limited(rate_key, max_requests, window_seconds):
                err_msg = message or f"Too many requests. Please wait a moment before trying again."
                
                # If AJAX / JSON request
                if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    resp = jsonify({
                        "ok": False,
                        "error": err_msg,
                        "retry_after": window_seconds
                    })
                    resp.status_code = 429
                    resp.headers["Retry-After"] = str(window_seconds)
                    return resp
                
                # Standard HTML response
                flash(f"⚠️ Rate limit reached: {err_msg}", "error")
                return Response(
                    render_template(
                        "errors/429.html",
                        retry_after=window_seconds,
                        message=err_msg
                    ),
                    status=429,
                    headers={"Retry-After": str(window_seconds)}
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def clear_rate_limits():
    """Testing helper to reset all rate limit counters."""
    with _lock:
        _request_records.clear()
