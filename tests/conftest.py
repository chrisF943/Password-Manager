"""
Pytest configuration and fixtures for password manager tests.
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up test environment variables before imports
os.environ['KEY'] = 'test_master_password'


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for testing."""
    # Create temp directory for test DB
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_pwm.db")

    # Override the database path before importing app
    import importlib
    from src.database import __init__ as db_init

    # Store original config
    original_uri = None
    if hasattr(db_init.app, 'config'):
        original_uri = db_init.app.config.get('SQLALCHEMY_DATABASE_URI')

    # Set test database URI
    db_init.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    # Recreate tables
    with db_init.app.app_context():
        db_init.db.create_all()

    yield db_path

    # Cleanup
    db_init.app.config['SQLALCHEMY_DATABASE_URI'] = original_uri

    # Remove temp files
    try:
        os.remove(db_path)
        os.rmdir(temp_dir)
    except:
        pass


@pytest.fixture
def cipher_suite():
    """Create a cipher suite for encryption tests."""
    from src.security.encryption import get_cipher_suite
    return get_cipher_suite(os.environ['KEY'])
