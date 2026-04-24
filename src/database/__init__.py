from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Initialize Flask app for database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pwm.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


def init_db():
    """Initialize the database, creating all tables if they don't exist."""
    with app.app_context():
        db.create_all()
