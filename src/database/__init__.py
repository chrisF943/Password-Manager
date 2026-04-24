from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from src.paths import DB_PATH, ensure_data_dir


class Base(DeclarativeBase):
    pass


# Ensure the data directory exists before configuring the DB
ensure_data_dir()

# Initialize Flask app for database using the absolute DB path
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


def init_db():
    """Initialize the database, creating all tables if they don't exist."""
    with app.app_context():
        db.create_all()
