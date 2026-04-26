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


def _set_sqlite_pragma():
    """Enable WAL mode for better concurrency and crash resilience."""
    from sqlalchemy import event, text
    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, "connect")
    def set_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


_set_sqlite_pragma()


def init_db():
    """Initialize the database, creating all tables if they don't exist."""
    with app.app_context():
        db.create_all()
