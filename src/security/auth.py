import hashlib
import hmac
import os

from dotenv import load_dotenv

from src.paths import ENV_FILE

# Load environment variables from the absolute path
load_dotenv(ENV_FILE)

# PBKDF2 verifier format: pbkdf2_sha256$<iterations>$<hex digest>
VERIFIER_PREFIX = "pbkdf2_sha256"
VERIFIER_ITERATIONS = 480_000


def _verifier_salt(salt: str) -> bytes:
    """Namespace the salt so the verifier can never equal the encryption key."""
    return f"verify:{salt}".encode()


def _derive_verifier(password: str, salt: str, iterations: int) -> str:
    digest = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        _verifier_salt(salt),
        iterations=iterations,
        dklen=32
    )
    return digest.hex()


def hash_master_password(password: str) -> str:
    """Derive a PBKDF2 verifier string for the master password."""
    from src.security.encryption import get_salt

    digest = _derive_verifier(password, get_salt(), VERIFIER_ITERATIONS)
    return f"{VERIFIER_PREFIX}${VERIFIER_ITERATIONS}${digest}"


def verify_master_password(input_password: str) -> bool:
    """Verify the master password against the stored verifier in .env.

    Accepts the legacy unsalted SHA-256 format and upgrades it in place.
    """
    stored = os.getenv("KEY")
    if stored is None:
        return False

    if stored.startswith(f"{VERIFIER_PREFIX}$"):
        from src.security.encryption import get_salt

        try:
            _, iterations, digest = stored.split("$")
            iterations = int(iterations)
        except ValueError:
            return False
        candidate = _derive_verifier(input_password, get_salt(), iterations)
        return hmac.compare_digest(candidate, digest)

    # Legacy: bare SHA-256 of the password
    legacy = hashlib.sha256(input_password.encode()).hexdigest()
    if not hmac.compare_digest(legacy, stored):
        return False

    _upgrade_legacy_key(input_password, stored)
    return True


def _upgrade_legacy_key(password: str, legacy_hash: str):
    """Replace a legacy SHA-256 KEY in .env with a PBKDF2 verifier.

    Only rewrites .env when it actually holds this legacy hash, so a KEY
    injected via the environment (tests) never overwrites real user data.
    """
    if not os.path.exists(ENV_FILE):
        return
    with open(ENV_FILE, "r") as f:
        if f"KEY={legacy_hash}" not in f.read():
            return

    from src.security.encryption import _replace_or_append_env_var

    new_hash = hash_master_password(password)
    _replace_or_append_env_var("KEY", new_hash)
    os.environ["KEY"] = new_hash
