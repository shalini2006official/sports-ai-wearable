from database.database import db
from database.models import WorkoutSession


def save_session(data):
    session = WorkoutSession(
        heart_rate=data.get("heart_rate"),
        spo2=data.get("spo2"),
        fatigue=data.get("fatigue"),
        performance=data.get("performance"),
        activity=data.get("activity"),
        posture=data.get("posture"),
        steps=data.get("steps"),
        cadence=data.get("cadence"),
        stride_length=data.get("stride_length"),
        temperature=data.get("temperature")
    )

    db.session.add(session)
    db.session.commit()


def get_all_sessions():
    return WorkoutSession.query.order_by(
        WorkoutSession.id.desc()
    ).all()

def get_latest_session():
    from database.models import WorkoutSession

    session = (
        WorkoutSession.query
        .order_by(WorkoutSession.id.desc())
        .first()
    )

    return session