# pyrefly: ignore [missing-import]
"""
routes/admin_routes.py — System Administration & User Management Panel

Enforces:
- @role_required('sysadmin')
- Staff account creation and deactivation (no public self-registration)
- Role assignment and status toggles
- Patient QR card issuance and inventory (never clinical visit data)
- Audit log inspection (read-only view of AccessLog table)
- STRICT PRIVACY: Visit and diagnosis notes are never imported or queried here
"""

import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from app.extensions import db
from app.models.user import User
from app.models.patient import Patient
from app.models.access_log import AccessLog
from app.models.application import Application
from app.middleware.role_required import role_required
from app.middleware.rate_limiter import rate_limit
from app.services.qr_service import (
    issue_patient_card,
    get_all_patient_cards,
    generate_qr_code,
)
from app.services.email_service import (
    send_staff_approval_email,
    send_staff_rejection_email,
    send_patient_approval_email,
    send_patient_rejection_email,
)

admin_routes = Blueprint("admin_routes", __name__, url_prefix="/admin")

VALID_ROLES = ["doctor", "pharmacist", "public_health_admin", "sysadmin"]


@admin_routes.route("/dashboard", methods=["GET"])
@role_required("sysadmin")
def dashboard():
    """System Administrator executive overview."""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_patients = Patient.query.count()
    total_logs = AccessLog.query.count()
    denied_logs = AccessLog.query.filter_by(result="denied").count()
    total_applications = Application.query.count()
    pending_applications = Application.query.filter_by(status="pending").count()

    recent_denials = (
        AccessLog.query.filter_by(result="denied")
        .order_by(AccessLog.timestamp.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        active_users=active_users,
        total_patients=total_patients,
        total_logs=total_logs,
        denied_logs=denied_logs,
        recent_denials=recent_denials,
        total_applications=total_applications,
        pending_applications=pending_applications,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Staff User Management & Role Assignment
# ─────────────────────────────────────────────────────────────────────────────

@admin_routes.route("/users", methods=["GET"])
@role_required("sysadmin")
def manage_users():
    """List staff accounts and user creation portal."""
    users = User.query.order_by(User.id.desc()).all()
    return render_template(
        "admin/manage_users.html",
        users=users,
        valid_roles=VALID_ROLES,
    )


@admin_routes.route("/users/create", methods=["POST"])
@role_required("sysadmin")
@rate_limit(max_requests=20, window_seconds=60, message="User creation rate limit reached. Please wait a minute.")
def create_user():
    """Create a new staff account (doctor, pharmacist, public health admin, sysadmin)."""
    username = request.form.get("username", "").strip()
    full_name = request.form.get("full_name", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "").strip()

    if not all([username, full_name, password, role]):
        flash("All fields (username, full name, password, role) are required.", "error")
        return redirect(url_for("admin_routes.manage_users"))

    if role not in VALID_ROLES:
        flash(f"Invalid role '{role}'. Must be one of {', '.join(VALID_ROLES)}.", "error")
        return redirect(url_for("admin_routes.manage_users"))

    if len(password) < 6:
        flash("Password must be at least 6 characters long.", "error")
        return redirect(url_for("admin_routes.manage_users"))

    if User.query.filter_by(username=username).first():
        flash(f"Username '{username}' already exists. Please choose a different username.", "error")
        return redirect(url_for("admin_routes.manage_users"))

    new_user = User(
        username=username,
        full_name=full_name,
        role=role,
        is_active=True,
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    flash(f"Staff account '{username}' successfully created with role '{role}'.", "success")
    return redirect(url_for("admin_routes.manage_users"))


@admin_routes.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@role_required("sysadmin")
def toggle_user_status(user_id: int):
    """Activate or deactivate a staff member."""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("Security violation: You cannot deactivate your own administrative account.", "error")
        return redirect(url_for("admin_routes.manage_users"))

    user.is_active = not user.is_active
    db.session.commit()

    state = "activated" if user.is_active else "deactivated"
    flash(f"User '{user.username}' has been {state}.", "info")
    return redirect(url_for("admin_routes.manage_users"))


@admin_routes.route("/users/<int:user_id>/role", methods=["GET", "POST"])
@role_required("sysadmin")
def role_assignment(user_id: int):
    """View and update role assignment for a staff member."""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        new_role = request.form.get("role", "").strip()
        if new_role not in VALID_ROLES:
            flash(f"Invalid role '{new_role}'.", "error")
            return redirect(url_for("admin_routes.role_assignment", user_id=user.id))

        if user.id == current_user.id and new_role != "sysadmin":
            flash("Security violation: You cannot revoke sysadmin role from your own session.", "error")
            return redirect(url_for("admin_routes.role_assignment", user_id=user.id))

        old_role = user.role
        user.role = new_role
        db.session.commit()

        flash(f"Updated role for '{user.username}' from {old_role} to {new_role}.", "success")
        return redirect(url_for("admin_routes.manage_users"))

    return render_template(
        "admin/role_assignment.html",
        user=user,
        valid_roles=VALID_ROLES,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Patient Card Issuance (QR Generator)
# ─────────────────────────────────────────────────────────────────────────────

@admin_routes.route("/patients/register", methods=["GET", "POST"])
@role_required("sysadmin")
def register_patient():
    """
    Issue a new encrypted patient QR card.
    Creates a new Patient record with encrypted PII and generates the printable QR card.
    Sysadmin manages card issuance only; no clinical visit data is accessible.
    """
    newly_issued = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not phone:
            flash("Patient full name and phone number are required to issue a card.", "error")
        else:
            try:
                patient, qr_data_uri = issue_patient_card(name, phone)
                newly_issued = {
                    "card_id": patient.card_id,
                    "name": name,
                    "phone": phone,
                    "qr_data_uri": qr_data_uri,
                }
                flash(f"Patient card issued successfully: {patient.card_id}", "success")
            except Exception as e:
                flash(f"Failed to issue patient card: {str(e)}", "error")

    issued_cards = get_all_patient_cards(limit=50)

    return render_template(
        "admin/register_patient.html",
        newly_issued=newly_issued,
        issued_cards=issued_cards,
    )


@admin_routes.route("/patients/<card_id>/qr", methods=["GET"])
@role_required("sysadmin")
def view_patient_qr(card_id: str):
    """Generate and return QR code data URI for an existing patient card."""
    patient = Patient.query.filter_by(card_id=card_id.strip()).first_or_404()
    qr_data_uri = generate_qr_code(patient.card_id)
    return {
        "card_id": patient.card_id,
        "qr_data_uri": qr_data_uri,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Immutable Audit Log Viewer
# ─────────────────────────────────────────────────────────────────────────────

@admin_routes.route("/audit-log", methods=["GET"])
@role_required("sysadmin")
def audit_log():
    """
    Read-only inspection interface for AccessLog audit trail.
    Displays every RBAC access decision, timestamp, endpoint, and outcome.
    """
    filter_result = request.args.get("result", "").strip() or None
    query = AccessLog.query

    if filter_result in ["allowed", "denied"]:
        query = query.filter_by(result=filter_result)

    logs = query.order_by(AccessLog.timestamp.desc()).limit(150).all()

    total_logs = AccessLog.query.count()
    allowed_count = AccessLog.query.filter_by(result="allowed").count()
    denied_count = AccessLog.query.filter_by(result="denied").count()

    return render_template(
        "admin/audit_log.html",
        logs=logs,
        filter_result=filter_result or "all",
        total_logs=total_logs,
        allowed_count=allowed_count,
        denied_count=denied_count,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Applications Screening & Processing (Step for Staff & Health Cards)
# ─────────────────────────────────────────────────────────────────────────────

@admin_routes.route("/applications", methods=["GET"])
@role_required("sysadmin")
def applications():
    """Review and screen public applications for Doctor, Pharmacist, and Health Cards."""
    status_filter = request.args.get("status", "all").strip().lower()
    role_filter = request.args.get("role", "all").strip().lower()

    query = Application.query

    if status_filter in ["pending", "approved", "rejected"]:
        query = query.filter_by(status=status_filter)
    if role_filter in ["doctor", "pharmacist", "patient"]:
        query = query.filter_by(role=role_filter)

    apps = query.order_by(Application.created_at.desc()).all()

    counts = {
        "all": Application.query.count(),
        "pending": Application.query.filter_by(status="pending").count(),
        "approved": Application.query.filter_by(status="approved").count(),
        "rejected": Application.query.filter_by(status="rejected").count(),
        "doctor": Application.query.filter_by(role="doctor").count(),
        "pharmacist": Application.query.filter_by(role="pharmacist").count(),
        "patient": Application.query.filter_by(role="patient").count(),
    }

    return render_template(
        "admin/applications.html",
        applications=apps,
        counts=counts,
        current_status=status_filter,
        current_role=role_filter,
    )


@admin_routes.route("/applications/<int:app_id>/approve", methods=["POST"])
@role_required("sysadmin")
def approve_application(app_id: int):
    """Approve application: create staff user account or issue patient QR card."""
    app_record = Application.query.get_or_404(app_id)

    if app_record.status == "approved":
        flash(f"Application {app_record.app_no} is already approved.", "info")
        return redirect(url_for("admin_routes.applications"))

    if app_record.role in ["doctor", "pharmacist"]:
        # Generate clean unique username
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", app_record.full_name.lower().replace("dr.", "").replace("dr", ""))[:12] or "staff"
        prefix = "dr" if app_record.role == "doctor" else "pharma"
        candidate_username = f"{prefix}_{clean_name}"

        suffix = 1
        final_username = candidate_username
        while User.query.filter_by(username=final_username).first():
            final_username = f"{candidate_username}_{suffix}"
            suffix += 1

        temp_password = f"Swasthya@{datetime.utcnow().year}"

        new_user = User(
            username=final_username,
            full_name=app_record.full_name,
            role=app_record.role,
            is_active=True,
        )
        new_user.set_password(temp_password)
        db.session.add(new_user)

        app_record.status = "approved"
        app_record.assigned_username = final_username
        app_record.assigned_password = temp_password
        app_record.reviewed_at = datetime.utcnow()
        db.session.commit()

        # Send approval email to doctor/pharmacist with credentials
        if app_record.email:
            send_staff_approval_email(
                app_record.email,
                app_record.full_name,
                app_record.role,
                final_username,
                temp_password,
            )

        flash(
            f"✅ Approved {app_record.full_name}! User account created. "
            f"Username: '{final_username}' | Password: '{temp_password}'",
            "success",
        )

    elif app_record.role == "patient":
        try:
            patient, _ = issue_patient_card(app_record.full_name, app_record.phone)
            app_record.status = "approved"
            app_record.assigned_card_id = patient.card_id
            app_record.reviewed_at = datetime.utcnow()
            db.session.commit()

            # Send approval email with e-card download & postal dispatch notice
            if app_record.email:
                send_patient_approval_email(app_record.email, app_record.full_name, patient.card_id)

            flash(
                f"✅ Approved Health Card for {app_record.full_name}! "
                f"Assigned Card ID: '{patient.card_id}'. QR card is now generated.",
                "success",
            )
        except Exception as e:
            flash(f"Failed to issue patient card: {str(e)}", "error")

    return redirect(url_for("admin_routes.applications"))


@admin_routes.route("/applications/<int:app_id>/reject", methods=["POST"])
@role_required("sysadmin")
def reject_application(app_id: int):
    """Reject an application with an administrative reason."""
    app_record = Application.query.get_or_404(app_id)
    reason = request.form.get("reason", "").strip() or "Verification failed or credentials could not be validated."

    app_record.status = "rejected"
    app_record.admin_notes = reason
    app_record.reviewed_at = datetime.utcnow()
    db.session.commit()

    # Send rejection notification email
    if app_record.email:
        if app_record.role in ["doctor", "pharmacist"]:
            send_staff_rejection_email(app_record.email, app_record.full_name, app_record.role, reason)
        else:
            send_patient_rejection_email(app_record.email, app_record.full_name, reason)

    flash(f"Application {app_record.app_no} rejected with note: {reason}", "info")
    return redirect(url_for("admin_routes.applications"))
