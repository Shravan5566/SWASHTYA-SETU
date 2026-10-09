# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """
    Staff account model for doctors, pharmacists, public health admins, and sysadmins.
    Patients are NEVER stored in this table (patients have no login credentials).
    """
    __tablename__ = "users"

    VALID_ROLES = ("doctor", "pharmacist", "public_health_admin", "sysadmin")

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # doctor, pharmacist, public_health_admin, sysadmin
    full_name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' role='{self.role}'>"


@login_manager.user_loader
def load_user(user_id: str):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))
