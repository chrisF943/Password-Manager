## Overview

A Python password manager app using Tkinter, SQLAlchemy and SQLite, that helps you manage and store your passwords
locally and securely. Built with Python, it provides an intuitive graphical interface for creating, retrieving,
updating, and deleting password entries. All passwords are encrypted using Fernet symmetric encryption to ensure your
sensitive information remains protected.

## Key Features

### Security

- **Encryption**: All passwords are encrypted using Fernet symmetric encryption
- **Authentication**: Application access protected by master password
- **Local Storage**: Data stored locally in SQLite database, not in the cloud
- **Key Management**: Automatic encryption key generation and storage for consistent data access

### Password Management

- **Store Passwords**: Save website, username, and password information
- **Search Functionality**: Quickly find passwords by website name
- **Update Passwords**: Easily update existing password entries
- **Delete Entries**: Remove password entries you no longer need

### User Experience

- **Password Generator**: Create strong, random passwords with a mix of letters, numbers, and symbols
- **Clipboard Integration**: Automatically copy generated passwords to clipboard
- **Modern UI**: Clean interface built with ttkbootstrap for an enhanced Tkinter experience
- **Password Counter**: Visual meter showing the number of stored passwords

### Technical Features

- **SQLAlchemy ORM**: Efficient database interactions
- **Environment Variables**: Secure configuration using .env files
- **Cryptography Library**: Industry-standard encryption using Python's cryptography package

## Getting Started

1. Navigate to the directory where you have cloned the project:
   ```bash
   cd path/to/project
   ```
   or on Windows:
   ```bash
   cd path\to\project
   ```
2. Create a virtual environment (You can skip to the next step if you already have one):
   ```bash
   python3 -m venv .venv
   ```
3. Activate your virtual environment:

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
    - *Optional* Verify packages are installed:
      ```bash
      pip list
      ```
5. Run the program:
   ```bash
   python3 main.py
   ```
6. When done, deactivate your virtual environment:
   ```bash
   deactivate
   ```

**_Developed on Python 3.12_**