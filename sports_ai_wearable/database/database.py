from flask import app
from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy object
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the SQLite database with the Flask app.
    """

    # SQLite database file
    import os

    # app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    #     "DATABASE_URL",
    #     "postgresql://postgres:Shalini%4023@localhost:5432/sports_ai"
    # )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sports_ai.db"

    # Disable modification tracking (improves performance)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Connect SQLAlchemy with Flask
    db.init_app(app)

    # Create all tables
    with app.app_context():
        db.create_all()