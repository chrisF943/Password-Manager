"""
Centralized app data directory resolution for fern.

Works in both dev mode (python main.py) and packaged mode (flet build).
All app data (database, .env config) is stored in the OS user data directory
so it survives app updates and is writable in a sandboxed environment.

macOS : ~/Library/Application Support/fern/
Windows: %APPDATA%\\fern\\
Linux  : ~/.local/share/fern/
"""
import os
import sys

APP_NAME = "fern"


def _get_data_dir() -> str:
    """Return the platform-appropriate writable data directory for fern."""
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(base, APP_NAME)


# The single writable data directory for all persistent files
DATA_DIR: str = _get_data_dir()

# Individual file paths derived from DATA_DIR
DB_PATH: str = os.path.join(DATA_DIR, "pwm.db")
ENV_FILE: str = os.path.join(DATA_DIR, ".env")
EXPORT_DIR: str = DATA_DIR  # CSV exports go here too


def ensure_data_dir() -> None:
    """Create the data directory if it doesn't exist yet."""
    os.makedirs(DATA_DIR, exist_ok=True)
