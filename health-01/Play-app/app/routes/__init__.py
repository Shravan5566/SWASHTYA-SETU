from .auth_routes import auth_routes
from .doctor_routes import doctor_routes
from .pharmacist_routes import pharmacist_routes
from .public_health_routes import public_health_routes
from .admin_routes import admin_routes
from .ai_routes import ai_routes
from .ajax_routes import ajax_routes
from .application_routes import application_routes

__all__ = [
    "auth_routes",
    "doctor_routes",
    "pharmacist_routes",
    "public_health_routes",
    "admin_routes",
    "ai_routes",
    "ajax_routes",
    "application_routes",
]
