# pyrefly: ignore [missing-import]
"""
routes/application_routes.py — Public Portal Applications

Dedicated routes for:
1. Citizen application for Swasthya Setu Digital Health Card (Patient) — /apply/health-card
2. Professional accreditation application for Doctor & Pharmacist — /apply/staff
3. Real-time application status tracker — /apply/status

Note: Public Health Administrator accounts are restricted and can ONLY
be provisioned directly by the System Administrator in the Admin console.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models.application import Application
from app.services.qr_service import generate_qr_code
from app.middleware.rate_limiter import rate_limit

application_routes = Blueprint("application_routes", __name__)

PUNE_LOCALITIES = [
    "Katraj",
    "Kothrud",
    "Hadapsar",
    "Viman Nagar",
    "Shivajinagar",
    "Baner",
    "Hinjewadi",
    "Swargate",
    "Pimpri",
    "Chinchwad",
    "Yerawada",
    "Camp",
    "Aundh",
    "Bibwewadi",
    "Sinhagad Road",
]


@application_routes.route("/apply/health-card", methods=["GET", "POST"])
@rate_limit(max_requests=15, window_seconds=60, message="Too many health card applications submitted from this network. Please wait a minute.")
def apply_health_card():
    """Dedicated page for citizen/patient digital health card application."""
    if request.method == "GET":
        return render_template("apply/health_card.html", pune_localities=PUNE_LOCALITIES)

    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    dob = request.form.get("dob", "").strip()
    gender = request.form.get("gender", "").strip()
    blood_group = request.form.get("blood_group", "").strip()
    gov_id_type = request.form.get("gov_id_type", "").strip()
    gov_id_number = request.form.get("gov_id_number", "").strip()
    locality = request.form.get("locality", "").strip()
    address = request.form.get("address", "").strip()
    emergency_name = request.form.get("emergency_name", "").strip()
    emergency_phone = request.form.get("emergency_phone", "").strip()
    emergency_relation = request.form.get("emergency_relation", "").strip()
    chronic_conditions = request.form.get("chronic_conditions", "").strip()
    allergies = request.form.get("allergies", "").strip()

    if not full_name or not phone or not locality:
        flash("Full name, phone number, and Pune locality are required fields.", "error")
        return render_template("apply/health_card.html", pune_localities=PUNE_LOCALITIES)

    app_no = Application.generate_app_no("patient")

    new_app = Application(
        app_no=app_no,
        app_type="health_card",
        role="patient",
        status="pending",
        full_name=full_name,
        email=email,
        phone=phone,
        dob=dob,
        gender=gender,
        blood_group=blood_group,
        gov_id_type=gov_id_type,
        gov_id_number=gov_id_number,
        locality=locality,
        address=address,
        emergency_name=emergency_name,
        emergency_phone=emergency_phone,
        emergency_relation=emergency_relation,
        chronic_conditions=chronic_conditions,
        allergies=allergies,
    )

    db.session.add(new_app)
    db.session.commit()

    flash(
        f"Application submitted successfully! Your tracking reference ID is {app_no}. "
        "The Pune Health Administration will verify your details and issue your card.",
        "success",
    )
    return redirect(url_for("application_routes.check_status", q=app_no))


@application_routes.route("/apply/staff", methods=["GET", "POST"])
@rate_limit(max_requests=15, window_seconds=60, message="Too many accreditation applications submitted. Please wait a minute.")
def apply_staff():
    """Dedicated page for healthcare professional accreditation application (Doctor or Pharmacist)."""
    if request.method == "GET":
        return render_template("apply/staff.html", pune_localities=PUNE_LOCALITIES)

    role = request.form.get("role", "").strip()
    if role not in ["doctor", "pharmacist"]:
        flash("Invalid staff role. Applications are open only for Doctors and Pharmacists.", "error")
        return render_template("apply/staff.html", pune_localities=PUNE_LOCALITIES)

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    council_reg_no = request.form.get("council_reg_no", "").strip()
    qualification = request.form.get("qualification", "").strip()
    specialization = request.form.get("specialization", "").strip()
    experience_years = request.form.get("experience_years", "").strip()
    workplace_name = request.form.get("workplace_name", "").strip()
    workplace_address = request.form.get("workplace_address", "").strip()
    locality = request.form.get("locality", "").strip()
    gov_id_type = request.form.get("gov_id_type", "").strip()
    gov_id_number = request.form.get("gov_id_number", "").strip()

    if not all([full_name, phone, email, council_reg_no, qualification, workplace_name, locality]):
        flash("All clinical verification fields marked with * are required.", "error")
        return render_template("apply/staff.html", pune_localities=PUNE_LOCALITIES)

    app_no = Application.generate_app_no(role)

    new_app = Application(
        app_no=app_no,
        app_type="staff",
        role=role,
        status="pending",
        full_name=full_name,
        email=email,
        phone=phone,
        council_reg_no=council_reg_no,
        qualification=qualification,
        specialization=specialization,
        experience_years=experience_years,
        workplace_name=workplace_name,
        workplace_address=workplace_address,
        locality=locality,
        gov_id_type=gov_id_type,
        gov_id_number=gov_id_number,
    )

    db.session.add(new_app)
    db.session.commit()

    role_title = "Doctor" if role == "doctor" else "Pharmacist"
    flash(
        f"{role_title} accreditation application submitted! Your tracking reference ID is {app_no}. "
        "The System Administrator will verify your Council registration and provision your account.",
        "success",
    )
    return redirect(url_for("application_routes.check_status", q=app_no))


@application_routes.route("/apply/ecard/download")
def download_ecard():
    """
    Render a beautiful, printable digital e-Card page for an approved patient.
    Accessed via /apply/ecard/download?q=<card_id or app_no>
    The browser's built-in print dialog is triggered automatically via JS.
    """
    query = request.args.get("q", "").strip()
    if not query:
        flash("Please provide a valid Card ID or Application Reference to download your e-Card.", "error")
        return redirect(url_for("application_routes.check_status"))

    app_record = (
        Application.query.filter(
            (Application.app_no.ilike(query))
            | (Application.assigned_card_id.ilike(query))
        )
        .filter_by(status="approved", role="patient")
        .first()
    )

    if not app_record:
        flash("No approved health card found for the provided reference. Please check your Application ID or Card ID.", "error")
        return redirect(url_for("application_routes.check_status", q=query))

    qr_data_uri = generate_qr_code(app_record.assigned_card_id)

    return render_template(
        "apply/ecard_download.html",
        card_id=app_record.assigned_card_id,
        full_name=app_record.full_name,
        blood_group=app_record.blood_group or "—",
        dob=app_record.dob or "—",
        gender=app_record.gender or "—",
        locality=app_record.locality or "Pune",
        emergency_name=app_record.emergency_name or "—",
        emergency_phone=app_record.emergency_phone or "—",
        emergency_relation=app_record.emergency_relation or "—",
        issued_date=app_record.reviewed_at.strftime("%d %b %Y") if app_record.reviewed_at else "—",
        qr_data_uri=qr_data_uri,
        app_no=app_record.app_no,
    )


@application_routes.route("/apply/status", methods=["GET", "POST"])
@rate_limit(max_requests=30, window_seconds=60, message="Status query rate limit reached. Please wait a minute.")
def check_status():
    """Dedicated status tracker page for application lookup by Ref No. or Phone."""
    query_param = request.values.get("q", "").strip()
    result = None

    if query_param:
        app_record = (
            Application.query.filter(
                (Application.app_no.ilike(query_param)) | (Application.phone == query_param)
            )
            .order_by(Application.created_at.desc())
            .first()
        )
        if app_record:
            qr_code = generate_qr_code(app_record.assigned_card_id) if app_record.assigned_card_id else None
            result = {
                "found": True,
                "app_no": app_record.app_no,
                "role": app_record.role,
                "full_name": app_record.full_name,
                "locality": app_record.locality,
                "status": app_record.status,
                "created_at": app_record.created_at.strftime("%d %b %Y, %I:%M %p"),
                "assigned_card_id": app_record.assigned_card_id,
                "assigned_username": app_record.assigned_username,
                "admin_notes": app_record.admin_notes,
                "qr_data_uri": qr_code,
                "blood_group": app_record.blood_group,
                "emergency_phone": app_record.emergency_phone,
                "dob": app_record.dob,
            }
        else:
            result = {"found": False, "query": query_param}

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify(result or {"found": False})

    return render_template("apply/status.html", status_result=result, query_param=query_param)
