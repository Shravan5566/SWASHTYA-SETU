# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.middleware.rate_limiter import rate_limit

auth_routes = Blueprint("auth_routes", __name__)


def get_role_dashboard(role: str) -> str:
    """Helper mapping role names to their respective landing endpoints."""
    role_destinations = {
        "doctor": "doctor_routes.dashboard",
        "pharmacist": "pharmacist_routes.scan",
        "public_health_admin": "public_health_routes.dashboard",
        "sysadmin": "admin_routes.dashboard",
    }
    target = role_destinations.get(role)
    if target:
        return url_for(target)
    return url_for("auth_routes.login")


@auth_routes.route("/login", methods=["GET", "POST"])
@rate_limit(max_requests=10, window_seconds=60, message="Too many login attempts. Please wait 1 minute before trying again.")
def login():
    """Shared login handler for doctor, pharmacist, public_health_admin, and sysadmin."""
    # If already logged in, redirect to their role dashboard immediately
    if current_user.is_authenticated:
        return redirect(get_role_dashboard(getattr(current_user, "role", "")))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "error")
            return render_template("auth/login.html"), 401

        if not user.is_active:
            flash("This account is currently deactivated. Please contact your system administrator.", "error")
            return render_template("auth/login.html"), 403

        # Authenticate with Flask-Login
        login_user(user)

        # Redirect according to role specification
        return redirect(get_role_dashboard(user.role))

    return render_template("auth/login.html")


@auth_routes.route("/logout")
@login_required
def logout():
    """Logs out the active user session."""
    logout_user()
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth_routes.login"))
