from datetime import datetime
from database.database import db


class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    heart_rate = db.Column(db.Float)
    spo2 = db.Column(db.Float)
    fatigue = db.Column(db.Float)
    performance = db.Column(db.Float)

    activity = db.Column(db.String(50))
    posture = db.Column(db.String(50))

    steps = db.Column(db.Integer)
    cadence = db.Column(db.Float)
    stride_length = db.Column(db.Float)
    temperature = db.Column(db.Float)