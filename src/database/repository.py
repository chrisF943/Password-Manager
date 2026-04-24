from src.database import db, app
from src.database.models import Passwords


def add_password(site: str, username: str, encrypted_password: str) -> Passwords:
    """Add a new password entry to the database."""
    with app.app_context():
        new_entry = Passwords(site=site, user=username, password=encrypted_password)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry


def get_password(site: str) -> Passwords | None:
    """Retrieve a password entry by website name."""
    with app.app_context():
        return Passwords.query.filter_by(site=site).first()


def get_all_passwords() -> list[Passwords]:
    """Retrieve all password entries."""
    with app.app_context():
        return Passwords.query.all()


def update_password(site: str, new_encrypted_password: str, new_username: str = None) -> bool:
    """Update an existing password entry. Returns True if successful."""
    with app.app_context():
        entry = Passwords.query.filter_by(site=site).first()
        if entry:
            entry.password = new_encrypted_password
            if new_username is not None:
                entry.user = new_username
            db.session.commit()
            return True
        return False


def delete_password(site: str) -> bool:
    """Delete a password entry. Returns True if successful."""
    with app.app_context():
        entry = Passwords.query.filter_by(site=site).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False


def get_entry_count() -> int:
    """Get the total number of stored password entries."""
    with app.app_context():
        return Passwords.query.count()
