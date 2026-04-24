import base64
import os
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

KEY_FILE = "encrypt_key.key"
SALT_LENGTH = 16


def get_salt() -> str:
    """Get salt from .env, generate and save if missing."""
    salt = os.getenv("SALT")
    if salt is None:
        salt = os.urandom(SALT_LENGTH).hex()
        _append_env_var("SALT", salt)
        os.environ["SALT"] = salt
    return salt


def _append_env_var(key: str, value: str):
    """Append a key=value line to the .env file."""
    with open(".env", "a") as f:
        f.write(f"\n{key}={value}\n")


def derive_key(master_password: str, salt: str) -> bytes:
    """Derive a Fernet key from master password and salt using PBKDF2."""
    key = hashlib.pbkdf2_hmac(
        'sha256',
        master_password.encode(),
        salt.encode(),
        iterations=480000,
        dklen=32
    )
    return base64.urlsafe_b64encode(key)


def get_cipher_suite(master_password: str) -> Fernet:
    """Derive and return a Fernet cipher suite from master password."""
    salt = get_salt()
    fernet_key = derive_key(master_password, salt)
    return Fernet(fernet_key)


def load_or_generate_key():
    """Legacy — removed. Use get_cipher_suite(master_password) instead."""
    raise NotImplementedError("load_or_generate_key is deprecated")


def encrypt_password(plaintext: str, cipher_suite: Fernet) -> str:
    """Encrypt a plaintext password."""
    return cipher_suite.encrypt(plaintext.encode()).decode()


def decrypt_password(encrypted: str, cipher_suite: Fernet) -> str:
    """Decrypt an encrypted password."""
    return cipher_suite.decrypt(encrypted.encode()).decode()


def needs_migration() -> bool:
    """Check if old key file exists and needs one-time migration."""
    return os.path.exists(KEY_FILE)


def migrateEncryption(master_password: str) -> bool:
    """
    One-time migration: decrypt all passwords with old key, re-encrypt with derived key.
    Returns True if migration was performed.
    """
    if not needs_migration():
        return False

    from src.database.repository import get_all_passwords, update_password

    # Load old cipher
    with open(KEY_FILE, "rb") as f:
        old_fernet_key = f.read()
    old_cipher = Fernet(old_fernet_key)

    # New derived cipher
    new_cipher = get_cipher_suite(master_password)

    # Re-encrypt all entries
    entries = get_all_passwords()
    for entry in entries:
        try:
            decrypted = decrypt_password(entry.password, old_cipher)
            new_encrypted = encrypt_password(decrypted, new_cipher)
            update_password(entry.site, new_encrypted, entry.user)
        except Exception:
            # If any entry fails, abort
            return False

    # Delete old key file after successful migration
    os.remove(KEY_FILE)
    return True