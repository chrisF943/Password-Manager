"""
Tests for authentication functionality.
"""
import hashlib
import os
from pathlib import Path

# Setup path before imports
project_root = Path(__file__).parent.parent
import sys

sys.path.insert(0, str(project_root))

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

# Set test environment - uses HASH comparison now
os.environ['KEY'] = _hash('test_master_password')


class TestAuthentication:
    """Test suite for master password authentication."""

    def test_verify_correct_password(self):
        """Test that correct password is verified."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('mysecretpassword')
        result = verify_master_password('mysecretpassword')
        assert result is True

    def test_verify_incorrect_password(self):
        """Test that incorrect password fails verification."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('mysecretpassword')
        result = verify_master_password('wrongpassword')
        assert result is False

    def test_verify_empty_password(self):
        """Test that empty password handling works."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('')
        result = verify_master_password('')
        assert result is True

    def test_verify_empty_password_fails_with_input(self):
        """Test that empty password fails with non-empty input."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('')
        result = verify_master_password('somepassword')
        assert result is False

    def test_verify_special_characters(self):
        """Test password with special characters."""
        from src.security.auth import verify_master_password

        test_password = "p@ssw0rd!#$%^&*()"
        os.environ['KEY'] = _hash(test_password)

        result = verify_master_password(test_password)
        assert result is True

    def test_verify_case_sensitive(self):
        """Test that password verification is case sensitive."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('MySecretPassword')

        assert verify_master_password('mysecretpassword') is False
        assert verify_master_password('MY SECRETPASSWORD') is False
        assert verify_master_password('MySecretPassword') is True

    def test_verify_no_key_set(self):
        """Test behavior when no KEY is set."""
        from src.security.auth import verify_master_password

        # Remove KEY from environment
        original = os.environ.pop('KEY', None)
        try:
            result = verify_master_password('anypassword')
            assert result is False
        finally:
            if original:
                os.environ['KEY'] = original

    def test_hash_master_password(self):
        """Test that hashing produces a PBKDF2 verifier string."""
        from src.security.auth import VERIFIER_ITERATIONS, hash_master_password

        result = hash_master_password('testpassword')
        prefix, iterations, digest = result.split('$')
        assert prefix == 'pbkdf2_sha256'
        assert int(iterations) == VERIFIER_ITERATIONS
        assert len(digest) == 64  # 32-byte derived key as hex

    def test_hash_is_salted(self):
        """Test that the verifier depends on the salt, not just the password."""
        from src.security.auth import hash_master_password

        first = hash_master_password('testpassword')
        os.environ['SALT'] = 'ffeeddccbbaa99887766554433221100'
        second = hash_master_password('testpassword')
        os.environ['SALT'] = '00112233445566778899aabbccddeeff'
        assert first != second

    def test_verifier_is_not_the_encryption_key(self):
        """Test that the stored verifier cannot be used as the Fernet key."""
        import base64

        from src.security.auth import hash_master_password
        from src.security.encryption import derive_key, get_salt

        digest = hash_master_password('testpassword').split('$')[2]
        fernet_key = derive_key('testpassword', get_salt())
        assert base64.urlsafe_b64encode(bytes.fromhex(digest)) != fernet_key

    def test_verify_pbkdf2_verifier(self):
        """Test round-trip verification with the PBKDF2 format."""
        from src.security.auth import hash_master_password, verify_master_password

        os.environ['KEY'] = hash_master_password('correct horse battery staple')
        assert verify_master_password('correct horse battery staple') is True
        assert verify_master_password('wrong horse battery staple') is False

    def test_verify_rejects_malformed_verifier(self):
        """Test that a corrupt verifier string fails instead of raising."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = 'pbkdf2_sha256$notanumber'
        assert verify_master_password('anything') is False

    def test_verify_accepts_legacy_sha256(self):
        """Test that legacy unsalted SHA-256 hashes still verify."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('legacypassword')
        assert verify_master_password('legacypassword') is True
        assert verify_master_password('otherpassword') is False
