import os
from cryptography.fernet import Fernet

KEY_FILE = "encrypt_key.key"


def load_or_generate_key() -> bytes:
    """Load existing encryption key or generate a new one."""
    try:
        if not os.path.exists(KEY_FILE):
            # Generate new key if file doesn't exist
            fernet_key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(fernet_key)
                print("Existing encryption key not found. New key created.")
        else:
            # Load existing key
            with open(KEY_FILE, "rb") as f:
                fernet_key = f.read()
                print("Existing encryption key found. Loading key.")
    except Exception as e:
        print(f"Error: {e}")
        fernet_key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(fernet_key)
            print("Unable to load existing key. New key created.")

    return fernet_key


def get_cipher_suite() -> Fernet | None:
    """Create and return a Fernet cipher suite."""
    fernet_key = load_or_generate_key()
    if fernet_key is not None:
        cipher_suite = Fernet(fernet_key)
        print("Cipher suite created.")
        return cipher_suite
    else:
        print("Unable to create cipher suite.")
        return None


def encrypt_password(plaintext: str, cipher_suite: Fernet) -> str:
    """Encrypt a plaintext password."""
    return cipher_suite.encrypt(plaintext.encode()).decode()


def decrypt_password(encrypted: str, cipher_suite: Fernet) -> str:
    """Decrypt an encrypted password."""
    return cipher_suite.decrypt(encrypted.encode()).decode()
