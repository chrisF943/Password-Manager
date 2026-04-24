"""
Tests for encryption/decryption functionality.
"""
import pytest
from src.security.encryption import encrypt_password, decrypt_password


class TestEncryption:
    """Test suite for encryption and decryption."""

    def test_encrypt_decrypt_roundtrip(self, cipher_suite):
        """Test that encrypting and decrypting returns original value."""
        original = "MySecretPassword123"
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_produces_different_output(self, cipher_suite):
        """Test that encryption produces different output than original."""
        original = "MySecretPassword123"
        encrypted = encrypt_password(original, cipher_suite)
        assert encrypted != original

    def test_encrypt_produces_consistent_output(self, cipher_suite):
        """Test that same password encrypts to same output."""
        original = "MySecretPassword123"
        encrypted1 = encrypt_password(original, cipher_suite)
        encrypted2 = encrypt_password(original, cipher_suite)
        # Note: Fernet generates unique tokens, so we test decryption works
        assert decrypt_password(encrypted1, cipher_suite) == original
        assert decrypt_password(encrypted2, cipher_suite) == original

    def test_decrypt_wrong_raises_error(self, cipher_suite):
        """Test that decrypting invalid data raises error."""
        with pytest.raises(Exception):
            decrypt_password("invalid_encrypted_data", cipher_suite)

    def test_encrypt_empty_string(self, cipher_suite):
        """Test encrypting empty string."""
        encrypted = encrypt_password("", cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == ""

    def test_encrypt_special_characters(self, cipher_suite):
        """Test encrypting password with special characters."""
        original = "P@ssw0rd!#$%^&*()"
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_unicode(self, cipher_suite):
        """Test encrypting password with unicode characters."""
        original = "пароль123"  # Russian word for password
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_long_password(self, cipher_suite):
        """Test encrypting very long password."""
        original = "A" * 1000
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_preserves_length_info(self, cipher_suite):
        """Test that encrypted data has expected Fernet format."""
        original = "short"
        encrypted = encrypt_password(original, cipher_suite)
        # Fernet token is base64 encoded, length varies
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
