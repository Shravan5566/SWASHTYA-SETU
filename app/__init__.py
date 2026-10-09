# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request
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

    # Register after_request audit logger hook
    app.after_request(audit_logger)

    # Prevent browser caching on dynamic/authenticated pages so back button won't show stale sessions
    @app.after_request
    def set_cache_headers(response):
        if not request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # 403 error handler — renders the RBAC denial page (Step 6)
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    # 429 error handler — renders rate limit exceeded page
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template("errors/429.html"), 429

    # Root route — Portal landing page & role navigation
    @app.route("/")
    def index():
        return render_template("index.html", pune_localities=PUNE_LOCALITIES)

    return app
