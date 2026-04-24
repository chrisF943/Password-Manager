## Overview

Welcome to lockey, a password manager built with Flet (Flutter), SQLAlchemy and SQLite, that helps you manage and store your passwords locally and securely. Built with Python, it provides an intuitive graphical interface for creating, retrieving, updating, and deleting password entries. All passwords are encrypted using Fernet symmetric encryption to ensure your sensitive information remains protected.

## Key Features

### Security

- **Key Derivation**: Encryption key derived from master password using PBKDF2 (480k iterations) — no key file stored on disk
- **Authentication**: Application access protected by master password
- **Local Storage**: Data stored locally in SQLite database, not in the cloud
- **Salt Management**: Unique salt generated per installation, stored in `.env`

### Password Management

- **Store Passwords**: Save website, username, and password information
- **Search Functionality**: Quickly find passwords by website name
- **Update Passwords**: Easily update existing password entries
- **Delete Entries**: Remove password entries you no longer need

### User Experience

- **Password Generator**: Create strong, random passwords with a mix of letters, numbers, and symbols
- **Password Strength Indicator**: Real-time visual feedback on password strength
- **Clipboard Integration**: Copy passwords to clipboard with one click
- **Modern UI**: Clean interface built with Flet (Flutter) for a polished, cross-platform experience
- **Password Counter**: Display showing the number of stored passwords
- **Export to CSV**: Export all passwords to a CSV file for backup

### Technical Features

- **Flet Framework**: Modern Python UI framework built on Flutter
- **SQLAlchemy ORM**: Efficient database interactions
- **Environment Variables**: Secure configuration using .env files
- **Cryptography Library**: Industry-standard encryption using Python's cryptography package

## Getting Started

1. Navigate to the project directory:
   ```bash
   cd path/to/Password-Manager
   ```

2. Create a virtual environment (optional if you already have one):
   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:

   For macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

   For Windows:
   ```bash
   .\.venv\Scripts\activate
   ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the program:
   ```bash
   python3 main.py
   ```

6. When done, deactivate your virtual environment:
   ```bash
   deactivate
   ```

## First-Time Setup

On first run, the application will:
- Initialize the SQLite database (`instance/pwm.db`)
- Generate a salt (`SALT` in `.env`)

You'll need to set your master password in the `.env` file:
```
KEY=your_master_password_here
SALT=will_be_generated_on_first_run
```

Or simply set `KEY` and the app will generate the salt automatically on first login.

## Project Structure

```
Password-Manager/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (KEY, SALT)
├── instance/
│   └── pwm.db              # SQLite database
└── src/
    ├── database/            # Database models and repository
    ├── security/            # Authentication and encryption
    ├── gui/                # Flet UI components
    └── utils/              # Password generator and strength checker
```

## Testing

The project includes a comprehensive test suite using pytest.

```bash
# Run all tests
pytest tests/

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

The test suite covers:
- **Authentication**: Master password verification (100% coverage)
- **Password Generator**: Password generation logic (100% coverage)
- **Password Strength**: Strength checking algorithm (100% coverage)
- **Encryption**: Encrypt/decrypt functionality including key derivation (tests added)

**_Developed on Python 3.12_**
