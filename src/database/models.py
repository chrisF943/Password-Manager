from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.database import db


class Passwords(db.Model):
    """Password entry model for storing website credentials."""
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site: Mapped[str] = mapped_column(String(100), nullable=False)  # Website or application name
    user: Mapped[str] = mapped_column(String(100), nullable=False)  # Username or email
    password: Mapped[str] = mapped_column(String(500), nullable=False)  # Increased for encrypted notes
    notes: Mapped[str] = mapped_column(String(500), nullable=True)  # New: optional notes
