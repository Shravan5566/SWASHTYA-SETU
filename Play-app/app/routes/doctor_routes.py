# pyrefly: ignore [missing-import]
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, flash
from flask_login import current_user
from app.middleware.role_required import role_required
from app.middleware.rate_limiter import rate_limit
from app.extensions import db
from app.models.patient import Patient
from app.models.visit import Visit
from app.services.qr_service import lookup_patient_by_card
from app.services.otp_service import validate_access_token
from app.config import DOCTOR_RECORD_EDIT_WINDOW_HOURS
from app.utils.crypto import decrypt

doctor_routes = Blueprint("doctor_routes", __name__, url_prefix="/doctor")


# ─────────────────────────────────────────────────────────────────────────────
# Helper: resolve patient and verify access token (used by history & add views)
# ─────────────────────────────────────────────────────────────────────────────
def _get_authorised_patient(patient_id: int) -> Patient:
    """
    Returns the Patient if the session holds a valid, unexpired access token
    for this exact doctor + patient pair. Aborts 403 otherwise.
    Server-side check on every load, not just once at OTP time.
    """
    token = session.get("patient_access_token")
    cached_pid = session.get("access_patient_id")

    if not token or cached_pid != patient_id:
        abort(403)

    if not validate_access_token(token, patient_id, current_user.id):
        session.pop("patient_access_token", None)
        session.pop("access_patient_id", None)
        abort(403)

    patient = Patient.query.get(patient_id)
    if patient is None:
        abort(404)
    return patient


# ─────────────────────────────────────────────────────────────────────────────
# Doctor dashboard
# ─────────────────────────────────────────────────────────────────────────────
@doctor_routes.route("/dashboard")
@role_required("doctor")
def dashboard():
    return redirect(url_for("doctor_routes.scan_qr"))


# ─────────────────────────────────────────────────────────────────────────────
# Step 7.2 — QR scan page (camera → ajax → OTP page)
# ─────────────────────────────────────────────────────────────────────────────
@doctor_routes.route("/scan")
@role_required("doctor")
def scan_qr():
    return render_template("doctor/scan_qr.html")


# ─────────────────────────────────────────────────────────────────────────────
# Step 7.3 — OTP verification page
# ─────────────────────────────────────────────────────────────────────────────
@doctor_routes.route("/otp-verify")
@role_required("doctor")
def otp_verify():
    if not session.get("otp_patient_id"):
        flash("Please scan a patient card first.", "info")
        return redirect(url_for("doctor_routes.scan_qr"))
    return render_template("doctor/otp_verify.html")


# ─────────────────────────────────────────────────────────────────────────────
# Step 7.5 — Patient history (verified token required on every load)
# ─────────────────────────────────────────────────────────────────────────────
@doctor_routes.route("/patient/<int:patient_id>/history")
@role_required("doctor")
def patient_history(patient_id: int):
    patient = _get_authorised_patient(patient_id)

    visits = (
        Visit.query
        .filter_by(patient_id=patient_id)
        .order_by(Visit.created_at.asc())
        .all()
    )

    # Determine which visits this doctor can delete (own + within window)
    cutoff = datetime.utcnow() - timedelta(hours=DOCTOR_RECORD_EDIT_WINDOW_HOURS)
    can_delete_visit_ids = {
        v.id for v in visits
        if v.created_by == current_user.id and v.created_at >= cutoff
    }

    # Step 7.6 AI summary — lazy import avoids error before Step 9 is built
    ai_summary = None
    try:
        from app.services.ai_service import get_summary
        ai_summary = get_summary(patient_id, visits)
    except Exception:
        pass  # AI service not ready yet (Step 9)

    try:
        patient_name = decrypt(patient.name_encrypted)
    except Exception:
        patient_name = "(encrypted)"

    return render_template(
        "doctor/patient_history.html",
        patient_id=patient_id,
        patient_name=patient_name,
        card_id=patient.card_id,
        visits=visits,
        ai_summary=ai_summary,
        can_delete_visit_ids=can_delete_visit_ids,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 7.7 — Add a new visit (GET = form, POST = save)
# ─────────────────────────────────────────────────────────────────────────────
@doctor_routes.route("/patient/<int:patient_id>/add-checkup", methods=["GET", "POST"])
@role_required("doctor")
@rate_limit(max_requests=30, window_seconds=60, message="Rate limit exceeded for adding checkups. Please wait a moment.")
def add_checkup(patient_id: int):
    patient = _get_authorised_patient(patient_id)

    try:
        card_id = patient.card_id
    except Exception:
        card_id = "—"

    if request.method == "POST":
        area = request.form.get("area", "").strip()
        diagnosis_notes = request.form.get("diagnosis_notes", "").strip()
        refill_restricted = bool(request.form.get("refill_restricted"))

        # Support multiple conditions / diseases
        conditions_list = request.form.getlist("conditions[]") or request.form.getlist("condition[]")
        if conditions_list:
            condition = ", ".join([c.strip() for c in conditions_list if c.strip()])
        else:
            condition = request.form.get("condition", "").strip()

        # Support multiple medicines & dosages
        meds_list = request.form.getlist("medicine[]")
        dose_list = request.form.getlist("dosage[]")
        inst_list = request.form.getlist("instructions[]")
        if meds_list and any(m.strip() for m in meds_list):
            med_parts = []
            dose_parts = []
            for i, m in enumerate(meds_list):
                m_clean = m.strip()
                if m_clean:
                    med_parts.append(m_clean)
                    d_clean = dose_list[i].strip() if i < len(dose_list) else ""
                    inst_clean = inst_list[i].strip() if inst_list and i < len(inst_list) else ""
                    combo_dose = f"{d_clean} ({inst_clean})" if inst_clean else d_clean
                    dose_parts.append(combo_dose or "As directed")
            medicine = ", ".join(med_parts)
            dosage = ", ".join(dose_parts)
        else:
            medicine = request.form.get("medicine", "").strip()
            dosage = request.form.get("dosage", "").strip()

        if not all([area, condition, medicine, dosage]):
            flash("Area, condition, medicine, and dosage are all required.", "error")
            return render_template("doctor/add_checkup.html",
                                   patient_id=patient_id, card_id=card_id)

        visit = Visit(
            patient_id=patient_id,
            created_by=current_user.id,
            area=area,
            condition=condition,
            diagnosis_notes=diagnosis_notes or None,
            medicine=medicine,
            dosage=dosage,
            refill_restricted=refill_restricted,
        )
        db.session.add(visit)

        # Invalidate cached AI summary so it regenerates on next history load
        try:
            from app.services.ai_service import invalidate_summary
            invalidate_summary(patient_id)
        except Exception:
            pass

        db.session.commit()
        flash("Checkup added successfully.", "success")
        return redirect(url_for("doctor_routes.patient_history", patient_id=patient_id))

    return render_template("doctor/add_checkup.html",
                           patient_id=patient_id, card_id=card_id)


# ─────────────────────────────────────────────────────────────────────────────
# Step 7.8 — Delete own recent visit (strict server-side rule — no client bypass)
# ─────────────────────────────────────────────────────────────────────────────
@doctor_routes.route("/visit/<int:visit_id>/delete", methods=["POST"])
@role_required("doctor")
def delete_visit(visit_id: int):
    visit = Visit.query.get_or_404(visit_id)

    # Rule 1: must be the author
    if visit.created_by != current_user.id:
        abort(403)

    # Rule 2: must be within the edit window
    cutoff = datetime.utcnow() - timedelta(hours=DOCTOR_RECORD_EDIT_WINDOW_HOURS)
    if visit.created_at < cutoff:
        abort(403)  # Past the edit window — immutable now

    # Rule 3: must hold a valid token for this patient
    patient = _get_authorised_patient(visit.patient_id)  # aborts 403 if invalid

    db.session.delete(visit)
    db.session.commit()
    flash("Visit record deleted.", "success")
    return redirect(url_for("doctor_routes.patient_history", patient_id=visit.patient_id))
