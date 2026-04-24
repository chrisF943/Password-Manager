import os
import hashlib
import hmac
from dotenv import load_dotenv
from src.paths import ENV_FILE

# Load environment variables from the absolute path
load_dotenv(ENV_FILE)


def verify_master_password(input_password: str) -> bool:
    """Verify the master password against the stored hash in .env."""
    stored_hash = os.getenv("KEY")
    if stored_hash is None:
        return False
    input_hash = hash_master_password(input_password)
    return hmac.compare_digest(input_hash, stored_hash)


def hash_master_password(password: str) -> str:
    """Hash the master password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()
