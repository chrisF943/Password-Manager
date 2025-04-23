import random
import ttkbootstrap as ttk
from tkinter import messagebox
import pyperclip
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from cryptography.fernet import Fernet
import getpass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# File to store encryption key
key_file = "encrypt_key.key"

# Initialize encryption key - either load existing or create new
try:
    if not os.path.exists(key_file):
        # Generate new key if file doesn't exist
        fernet_key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(fernet_key)
            print("Existing encryption key not found. New key created.")
    else:
        # Load existing key
        with open(key_file, "rb") as f:
            fernet_key = f.read()
            print("Existing encryption key found. Loading key.")
except Exception as e:
    # Fallback if key loading fails
    print(f"Error: {e}")
    fernet_key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(fernet_key)
        print("Unable to load existing key. New key created.")

# Create cipher suite for encryption/decryption
if fernet_key is not None:
    cipher_suite = Fernet(fernet_key)
    print("Cipher suite created.")
else:
    print("Unable to create cipher suite.")


# SQLAlchemy base class for models
class Base(DeclarativeBase):
    pass


# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pwm.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Password entry model
class Passwords(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site: Mapped[str] = mapped_column(String(100), nullable=False)  # Website or application name
    user: Mapped[str] = mapped_column(String(100), nullable=False)  # Username or email
    password: Mapped[str] = mapped_column(String(100), nullable=False)  # Encrypted password


# Uncomment to initialize database on first run
# with app.app_context():
#     db.create_all()


# Generate a random password with specific character requirements
def generate_pw():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    nr_letters = random.randint(6, 6)
    nr_symbols = random.randint(3, 3)
    nr_numbers = random.randint(3, 3)

    password_letters = [random.choice(letters) for _ in range(nr_letters)]
    password_symbols = [random.choice(symbols) for _ in range(nr_symbols)]
    password_numbers = [random.choice(numbers) for _ in range(nr_numbers)]

    password_list = password_letters + password_numbers + password_symbols

    random.shuffle(password_list)

    # Create final password string
    password = "".join(password_list)
    pw_text.insert(0, password)
    pyperclip.copy(password)


# Update the password count meter
def get_entry_count():
    with app.app_context():
        count = Passwords.query.count()
        entries_meter.configure(amountused=count)
        entries_meter.configure(subtext=f"Stored Passwords: {count}")


# Save new password entry to database
def fetch_fields():
    # Validate that all fields are filled
    if len(web_text.get()) == 0 or len(user_text.get()) == 0 or len(pw_text.get()) == 0:
        messagebox.showwarning(title="Error", message="You have left a field blank.")
    else:
        # Encrypt password before storing
        encrypted_pw = cipher_suite.encrypt(pw_text.get().encode()).decode()
        new_entry = Passwords(
            site=web_text.get(),
            user=user_text.get(),
            password=encrypted_pw
        )

        with app.app_context():
            db.session.add(new_entry)
            db.session.commit()

        # Clear input fields
        web_text.delete(0, ttk.END)
        pw_text.delete(0, ttk.END)

        get_entry_count()
        messagebox.showinfo(title="Success", message="Entry added.")


# Search for password by website name
def search():
    with app.app_context():
        # Find entry matching website name
        search_entry = Passwords.query.filter_by(site=web_text.get()).first()
        if search_entry:
            # Decrypt password for display
            decrypted_pw = cipher_suite.decrypt(search_entry.password.encode()).decode()
            messagebox.showinfo(title=web_text.get(),
                                message=f"Username: {search_entry.user}\nPassword: {decrypted_pw}")
        else:
            messagebox.showwarning(title="Error", message="No entry found.")


# Update existing password
def update():
    with app.app_context():
        # Find entry matching website name
        search_entry = Passwords.query.filter_by(site=web_text.get()).first()
        if search_entry:
            # Encrypt and update password
            new_pw = cipher_suite.encrypt(pw_text.get().encode()).decode()
            search_entry.password = new_pw
            db.session.commit()

            web_text.delete(0, ttk.END)
            pw_text.delete(0, ttk.END)
            messagebox.showinfo(title="Success", message="Password updated.")
        else:
            messagebox.showwarning(title="Error", message="No entry found.")


# Delete password entry
def delete():
    with app.app_context():
        # Find entry matching website name
        search_entry = Passwords.query.filter_by(site=web_text.get()).first()
        if search_entry:
            db.session.delete(search_entry)
            db.session.commit()

            web_text.delete(0, ttk.END)
            get_entry_count()
            messagebox.showinfo(title="Success", message="Entry deleted.")
        else:
            messagebox.showwarning(title="Error", message="No entry found.")


# Authentication loop - requires correct password from .env file
auth = ""
while auth != os.getenv("KEY"):
    # Hides password input when running in terminal
    auth = getpass.getpass("Enter Password: ")
    if auth == os.getenv("KEY"):
        print("Welcome to your Password Manager")

        # Initialize main application window
        window = ttk.Window(themename="solar")
        window.title("Password Manager")
        window.config(padx=50, pady=50)

        canvas = ttk.Canvas(width=200, height=200)
        background_img = ttk.PhotoImage(file="/Users/chrisfaris/Desktop/python/Password Manager/images/lock.png")
        canvas.create_image(100, 100, image=background_img)
        canvas.grid(column=2, row=1)

        welcome_label = ttk.Label(text="Welcome to your Password Manager", font=("Arial", 16, "bold"))
        welcome_label.grid(column=1, row=0)

        # Password count meter
        entries_meter = ttk.Meter(
            window,
            bootstyle="info",
            amountused=0,
            amounttotal=100,
            metersize=180,
            stripethickness=10,
            interactive=False
        )
        entries_meter.grid(column=1, row=1)

        # Update the meter immediately when GUI opens
        get_entry_count()

        web_label = ttk.Label(text="Website:")
        web_label.grid(column=0, row=2)
        web_text = ttk.Entry(width=35, bootstyle="info")
        web_text.focus()
        web_text.grid(column=1, row=2, sticky="EW")

        user_label = ttk.Label(text="Email/Username:")
        user_label.grid(column=0, row=3)
        user_text = ttk.Entry(width=35, bootstyle="info")
        user_text.grid(column=1, row=3, sticky="EW")

        pw_label = ttk.Label(text="Password:")
        pw_label.grid(column=0, row=4)
        pw_text = ttk.Entry(width=21, bootstyle="info")
        pw_text.grid(column=1, row=4, sticky="EW")

        search_button = ttk.Button(text="Search", command=search, bootstyle="info")
        search_button.grid(column=2, row=2, sticky="EW")

        update_button = ttk.Button(text="Update", command=update, bootstyle="warning")
        update_button.grid(column=2, row=4, sticky="EW")

        delete_button = ttk.Button(text="Delete", command=delete, bootstyle="danger")
        delete_button.grid(column=2, row=5, sticky="EW")

        generate_button = ttk.Button(text="Generate Password", command=generate_pw, bootstyle="light")
        generate_button.grid(column=2, row=3, sticky="EW")

        add_button = ttk.Button(text="Add", command=fetch_fields, bootstyle="success")
        add_button.grid(column=1, row=5, sticky="EW")

        # Start the GUI event loop
        window.mainloop()

    else:
        print("Incorrect Password")
        retry = input("Would you like to try again? (Y/N): ").upper()
        if retry != 'Y':
            print("Exiting program...")
            break
