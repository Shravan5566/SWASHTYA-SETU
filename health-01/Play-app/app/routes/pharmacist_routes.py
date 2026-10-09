# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.middleware.role_required import role_required
from app.middleware.rate_limiter import rate_limit
from app.services.qr_service import lookup_patient_by_card
from app.extensions import db
from app.models.visit import Visit

pharmacist_routes = Blueprint("pharmacist_routes", __name__, url_prefix="/pharmacist")


@pharmacist_routes.route("/scan", methods=["GET", "POST"])
@role_required("pharmacist")
@rate_limit(max_requests=30, window_seconds=60, message="Pharmacist scan rate limit reached. Please wait a moment.")
def scan():
    """QR scan landing page. POST receives a card_id and redirects to the medicine view."""
    if request.method == "POST":
        card_id = request.form.get("card_id", "").strip()
        if not card_id:
            flash("Please enter or scan a card ID.", "error")
            return render_template("pharmacist/scan.html")

        patient = lookup_patient_by_card(card_id)
        if patient is None:
            flash("Patient card not recognised. Please check and try again.", "error")
            return render_template("pharmacist/scan.html")

        return redirect(url_for("pharmacist_routes.medicine_view", patient_id=patient.id))

    return render_template("pharmacist/scan.html")


@pharmacist_routes.route("/patient/<int:patient_id>/medicines")
@role_required("pharmacist")
def medicine_view(patient_id: int):
    """
    Read-only medicine view.
    Selects ONLY four columns from Visit: card_id (via patient), created_at, condition, medicine.
    diagnosis_notes is NEVER fetched — not selected in the query at all.
    No create/update/delete routes exist in this blueprint by construction.
    """
    from app.models.patient import Patient

    patient = Patient.query.get_or_404(patient_id)

    # Explicitly select only the four allowed columns — diagnosis_notes is never touched
    rows = (
        db.session.query(
            Visit.id,
            Visit.created_at,
            Visit.condition,
            Visit.medicine,
            Visit.refill_restricted,
        )
        .filter(Visit.patient_id == patient_id)
        .order_by(Visit.created_at.desc())
        .all()
    )

    return render_template(
        "pharmacist/medicine_view.html",
        card_id=patient.card_id,
        patient_id=patient_id,
        rows=rows,
    )

# ── No create / update / delete routes — pharmacist is view-only by construction ──
