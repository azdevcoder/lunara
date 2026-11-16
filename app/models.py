from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date)
    goal = db.Column(db.String(40), default="ciclo")
    cycle_length = db.Column(db.Integer, default=28)
    period_length = db.Column(db.Integer, default=5)
    last_period_start = db.Column(db.Date)
    onboarding_done = db.Column(db.Boolean, default=False, nullable=False)
    pregnancy_mode = db.Column(db.Boolean, default=False, nullable=False)
    due_date = db.Column(db.Date)
    contraceptive = db.Column(db.String(120))
    contraceptive_time = db.Column(db.String(5), default="21:00")
    notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)
    reminder_time = db.Column(db.String(5), default="09:00")
    theme = db.Column(db.String(20), default="rose", nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    logs = db.relationship(
        "DailyLog", backref="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    def initials(self):
        parts = [p for p in (self.name or "").split() if p]
        if not parts:
            return "L"
        if len(parts) == 1:
            return parts[0][:1].upper()
        return (parts[0][:1] + parts[-1][:1]).upper()

    def first_name(self):
        return (self.name or "").split()[0] if self.name else "você"


class DailyLog(db.Model):
    __tablename__ = "daily_logs"
    __table_args__ = (
        db.UniqueConstraint("user_id", "log_date", name="uq_user_log_date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    log_date = db.Column(db.Date, nullable=False, index=True)
    flow = db.Column(db.String(20))
    symptoms = db.Column(db.JSON, default=list)
    moods = db.Column(db.JSON, default=list)
    energy = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    water_ml = db.Column(db.Integer, default=0)
    weight_kg = db.Column(db.Float)
    temperature = db.Column(db.Float)
    sex = db.Column(db.String(30))
    discharge = db.Column(db.String(30))
    cravings = db.Column(db.String(120))
    exercise = db.Column(db.String(160))
    medication = db.Column(db.String(160))
    pill_taken = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    def symptom_list(self):
        return self.symptoms or []

    def mood_list(self):
        return self.moods or []
