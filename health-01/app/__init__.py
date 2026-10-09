import os
from flask import Flask, render_template, request, send_from_directory, redirect
from app.config import Config
from app.extensions import db, login_manager
from app.middleware import audit_logger
from app.routes import (
    auth_routes,
    doctor_routes,
    pharmacist_routes,
    public_health_routes,
    admin_routes,
    ai_routes,
    ajax_routes,
    application_routes,
    api_routes,
)
from app.routes.application_routes import PUNE_LOCALITIES


def create_app(config_class=Config):
    """Application factory for Swasthya Setu."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth_routes.login"
    login_manager.login_message_category = "info"

    # Ensure models are loaded
    from app import models  # noqa: F401

    # Register blueprints
    app.register_blueprint(auth_routes)
    app.register_blueprint(doctor_routes)
    app.register_blueprint(pharmacist_routes)
    app.register_blueprint(public_health_routes)
    app.register_blueprint(admin_routes)
    app.register_blueprint(ai_routes)
    app.register_blueprint(ajax_routes)
    app.register_blueprint(application_routes)
    app.register_blueprint(api_routes)

    # Register after_request audit logger hook
    app.after_request(audit_logger)

    # CORS & Preflight handler for modern SPA frontend
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            from flask import make_response
            res = make_response()
            origin = request.headers.get("Origin") or "*"
            res.headers["Access-Control-Allow-Origin"] = origin
            res.headers["Access-Control-Allow-Credentials"] = "true"
            res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            res.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            return res

    # Prevent browser caching on dynamic/authenticated pages and set CORS
    @app.after_request
    def set_cache_and_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        if not request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # 403 error handler — renders the RBAC denial page
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    # 429 error handler — renders rate limit exceeded page
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template("errors/429.html"), 429

    # Locate modern React frontend dist build
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_folder = os.path.join(base_dir, "dist")
    if not os.path.exists(dist_folder):
        dist_folder = os.path.abspath(os.path.join(base_dir, "..", "..", "dist"))

    # Static asset routes for modern React bundle
    @app.route("/assets/<path:filename>")
    def serve_dist_assets(filename):
        return send_from_directory(os.path.join(dist_folder, "assets"), filename)

    @app.route("/<string:filename>")
    def serve_dist_file(filename):
        target = os.path.join(dist_folder, filename)
        if os.path.isfile(target):
            return send_from_directory(dist_folder, filename)
        if filename.startswith("api"):
            return "Not Found", 404
        if os.path.exists(os.path.join(dist_folder, "index.html")):
            return send_from_directory(dist_folder, "index.html")
        return "Not Found", 404

    # Root route — Serves modern React frontend SPA directly
    @app.route("/")
    def index():
        if os.path.exists(os.path.join(dist_folder, "index.html")):
            return send_from_directory(dist_folder, "index.html")
        return render_template("index.html", pune_localities=PUNE_LOCALITIES)

    # Seamless redirects from old Jinja pages to new Figma SPA routes
    @app.route("/apply/health-card", methods=["GET"])
    def redirect_apply_health_card():
        return redirect("/#/apply")

    @app.route("/apply/status", methods=["GET"])
    def redirect_apply_status():
        return redirect("/#/track")

    @app.route("/apply/staff", methods=["GET"])
    def redirect_apply_staff():
        return redirect("/#/apply")

    @app.route("/doctor/scan", methods=["GET"])
    @app.route("/doctor/dashboard", methods=["GET"])
    @app.route("/doctor/otp-verify", methods=["GET"])
    def redirect_doctor():
        return redirect("/#/doctor")

    @app.route("/pharmacist/scan", methods=["GET"])
    @app.route("/pharmacist/dashboard", methods=["GET"])
    def redirect_pharmacist():
        return redirect("/#/pharmacist")

    @app.route("/public-health/dashboard", methods=["GET"])
    @app.route("/public-health/trend-forecast", methods=["GET"])
    def redirect_public_health():
        return redirect("/#/surveillance")

    @app.route("/admin/dashboard", methods=["GET"])
    def redirect_admin():
        return redirect("/#/admin")

    return app
