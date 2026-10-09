from app.extensions import db


class Stats(db.Model):
    """
    Precomputed public health aggregate statistics table.
    The public health anonymizer reads from this table to enforce MIN_GROUP_SIZE privacy rules.
    """
    __tablename__ = "stats"

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False, index=True)
    condition = db.Column(db.String(100), nullable=False, index=True)
    time_bucket = db.Column(db.String(50), nullable=False, index=True)  # e.g., '2026-W38'
    count = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Stats id={self.id} area='{self.area}' condition='{self.condition}' count={self.count}>"
