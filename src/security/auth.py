import os
import hashlib
import hmac
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def verify_master_password(input_password: str) -> bool:
    """Verify the master password against the stored password in .env."""
    stored_key = os.getenv("KEY")
    if stored_key is None:
        return False
    return hmac.compare_digest(input_password, stored_key)


def hash_master_password(password: str) -> str:
    """Hash the master password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()
