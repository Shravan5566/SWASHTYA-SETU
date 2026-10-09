from datetime import datetime
from app.extensions import db


class AccessLog(db.Model):
    """
    Immutable audit log recording every request or access attempt.
    Tracks user, role, endpoint, outcome (allowed / denied), and timestamp.
    """
    __tablename__ = "access_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    role_at_time = db.Column(db.String(50), nullable=True)
    endpoint = db.Column(db.String(255), nullable=False)
    result = db.Column(db.String(20), nullable=False)  # 'allowed' or 'denied'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship to User (nullable for unauthenticated attempts)
    user = db.relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AccessLog id={self.id} user_id={self.user_id} endpoint='{self.endpoint}' result='{self.result}'>"
