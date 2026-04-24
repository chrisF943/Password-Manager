## Overview

Welcome to **fern**, a password manager built with Flet (Flutter), SQLAlchemy and SQLite, that helps you manage and store your passwords locally and securely. All passwords are encrypted using Fernet symmetric encryption to ensure your sensitive information remains protected.

## Key Features

### Security

- **Key Derivation**: Encryption key derived from master password using PBKDF2 (480k iterations) — no key file stored on disk
- **Authentication**: Application access protected by master password (stored as SHA-256 hash)
- **Local Storage**: Data stored locally in SQLite database, not in the cloud
- **Salt Management**: Unique salt generated per installation, stored alongside database
- **Auto-Lock**: App automatically locks after 3 minutes of inactivity

### Password Management

- **Notes Field**: Add optional notes to each password entry (e.g., security question answers)
- **Store Passwords**: Save website, username, password, and notes
- **Search Functionality**: Quickly find passwords by website name with A-Z / Z-A sort toggle
- **Update Passwords**: Easily update existing password entries
- **Delete Entries**: Remove password entries with confirmation
- **Export to CSV**: Export all passwords to a CSV file for backup

### User Experience

- **First-Time Setup Wizard**: On first launch, guided master password creation
- **Password Generator**: Create strong, random passwords with a mix of letters, numbers, and symbols
- **Password Strength Indicator**: Real-time visual feedback on password strength
- **Clipboard Integration**: Copy passwords to clipboard with one click
- **Modern UI**: Clean interface built with Flet (Flutter) for a polished, cross-platform experience
- **Password Counter**: Display showing the number of stored passwords
- **Dark Theme**: Modern dark UI using Flet

## Getting Started

1. Navigate to the project directory:
   ```bash
   cd Password-Manager
   ```

2. Create and activate a virtual environment (optional if you already have one):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the program:
   ```bash
   python3 main.py
   ```

5. On first run, enter your new master password in the setup wizard.

## First-Time Setup

On first launch with no existing `.env` file, the app shows a **setup wizard** where you:
1. Create a master password (with strength indicator)
2. Confirm the password
3. The app generates a unique salt and stores everything

Your data is stored at:
- **macOS**: `~/Library/Application Support/fern/`
- **Windows**: `%APPDATA%\fern\`
- **Linux**: `~/.local/share/fern/`

## Project Structure

```
Password-Manager/
├── main.py                    # Application entry point (login/main view switching)
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Flet build configuration
├── src/
│   ├── paths.py              # Centralized OS data path resolution
│   ├── database/
│   │   ├── __init__.py      # Flask app & SQLAlchemy db init
│   │   ├── models.py        # Passwords model (site, user, password, notes)
│   │   └── repository.py    # CRUD operations
│   ├── security/
│   │   ├── auth.py          # Master password verification (hashed comparison)
│   │   └── encryption.py    # Fernet encryption, PBKDF2 key derivation
│   ├── gui/
│   │   └── popups.py        # Delete/Update/Search/Settings dialogs
│   └── utils/
│       ├── password_gen.py        # Password generator
│       └── password_strength.py   # Password strength checker
└── tests/                    # pytest test suite
```

## Testing

```bash
# Run all tests
pytest tests/

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

The test suite covers authentication, password generation, password strength checking, and encryption.

**Developed on Python 3.12**
