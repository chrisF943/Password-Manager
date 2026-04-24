"""
Main application entry point with single-window login/main view switching.
"""
import flet as ft
from src.database import init_db
from src.security.auth import verify_master_password
from src.database.repository import (
    add_password, get_all_passwords, get_password,
    update_password as repo_update_password,
    delete_password as repo_delete_password,
    get_entry_count
)
from src.security.encryption import get_cipher_suite, encrypt_password, decrypt_password, needs_migration, migrateEncryption
from src.utils.password_gen import generate_password
from src.utils.password_strength import check_password_strength
from src.gui.popups import show_delete_popup, show_update_popup, show_search_popup, show_settings_popup


def main(page: ft.Page):
    """Main application with login state switching."""
    page.title = "fern"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 900
    page.window.height = 750
    page.window.resizable = True

    # Track login state and master password
    is_logged_in = {"value": False}
    master_password_session = {"value": ""}

    def show_login_view():
        """Show the login view."""
        is_logged_in["value"] = False
        master_password_session["value"] = ""

        error_message = ft.Text("", color=ft.Colors.ERROR, visible=False)
        password_field = ft.TextField(
            label="Master Password",
            password=True,
            can_reveal_password=True,
            text_size=16,
        )

        def on_login_click(e):
            password = password_field.value
            if not password:
                error_message.value = "Please enter a password"
                error_message.visible = True
                page.update()
                return

            if verify_master_password(password):
                is_logged_in["value"] = True
                master_password_session["value"] = password
                password_field.value = ""
                error_message.visible = False
                show_main_view()
            else:
                error_message.value = "Incorrect password"
                error_message.visible = True
                password_field.value = ""
            page.update()

        password_field.on_submit = on_login_click

        fern_icon = ft.Icon(ft.Icons.FOREST, size=80, color=ft.Colors.BLUE_400)

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        fern_icon,
                        ft.Text("fern", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Enter your master password", size=14, color=ft.Colors.WHITE54),
                        ft.Container(height=20),
                        password_field,
                        error_message,
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.FOREST, size=20), ft.Text("Unlock")],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            width=200,
                            height=45,
                            on_click=on_login_click,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                alignment=ft.alignment.Alignment(0, 0),
                expand=True,
                padding=30,
            )
        )

    def show_main_view():
        """Show the main password manager view."""
        is_logged_in["value"] = True

        # Check for migration needed
        if needs_migration():
            try:
                migrateEncryption(master_password_session["value"])
                print("Migration complete. Old key file deleted.")
            except Exception as e:
                print(f"Migration failed: {e}")
                # Continue with old cipher anyway — don't block the user

        # Initialize cipher suite using session master password
        cipher_suite = get_cipher_suite(master_password_session["value"])

        # Status message
        status_text = ft.Text("", size=14, color=ft.Colors.GREEN_400)

        # Password strength indicator
        strength_bar = ft.Container(
            content=ft.Row([
                ft.Container(
                    width=100,
                    height=6,
                    bgcolor=ft.Colors.GREY_800,
                    border_radius=3,
                    content=ft.Container(width=0, bgcolor=ft.Colors.GREY_600, border_radius=3),
                ),
                strength_text := ft.Text("", size=12),
            ], spacing=10),
            visible=False,
        )

        def on_password_change(e):
            password = password_field.value
            if not password:
                strength_bar.visible = False
            else:
                strength = check_password_strength(password)
                strength_bar.visible = True
                bar = strength_bar.content.controls[0]
                bar.content.width = int(strength["score"] * 25)
                bar.content.bgcolor = strength["color"]
                strength_text.value = strength["message"]
                strength_text.color = strength["color"]
            page.update()

        # Form fields
        site_field = ft.TextField(label="Website / App Name", text_size=14, expand=1)
        username_field = ft.TextField(label="Username / Email", text_size=14, expand=1)
        password_field = ft.TextField(
            label="Password", password=True, can_reveal_password=True, text_size=14, expand=1,
            on_change=on_password_change,
        )

        # Password count display
        count_text = ft.Text("", size=14, color=ft.Colors.WHITE70)

        def update_count():
            count = get_entry_count()
            count_text.value = f"Total passwords stored: {count}"
            page.update()

        def on_add_click(e):
            site = site_field.value.strip()
            username = username_field.value.strip()
            password = password_field.value

            if not site or not username or not password:
                status_text.value = "Please fill in all fields"
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            existing = get_password(site)
            if existing:
                status_text.value = f"Entry for '{site}' already exists. Use Update to modify."
                status_text.color = ft.Colors.ORANGE_400
                page.update()
                return

            encrypted = encrypt_password(password, cipher_suite)
            add_password(site, username, encrypted)

            site_field.value = ""
            username_field.value = ""
            password_field.value = ""
            strength_bar.visible = False
            status_text.value = f"Password for '{site}' added successfully!"
            status_text.color = ft.Colors.GREEN_400
            update_count()
            page.update()

        def on_generate_click(e):
            generated = generate_password()
            password_field.value = generated
            on_password_change(None)
            status_text.value = "Password generated!"
            status_text.color = ft.Colors.BLUE_400
            page.update()

        def on_search_click(e):
            show_search_popup(page, cipher_suite)

        def on_update_click(e):
            show_update_popup(page, cipher_suite, update_count)

        def on_delete_click(e):
            show_delete_popup(page, update_count)

        def on_export_click(e):
            import csv
            import os
            try:
                entries = get_all_passwords()
                if not entries:
                    status_text.value = "No passwords to export"
                    status_text.color = ft.Colors.ORANGE_400
                    page.update()
                    return

                export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance")
                export_path = os.path.join(export_dir, "passwords_export.csv")

                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Site", "Username", "Password"])
                    for entry in entries:
                        try:
                            decrypted = decrypt_password(entry.password, cipher_suite)
                        except:
                            decrypted = "***"
                        writer.writerow([entry.site, entry.user, decrypted])

                status_text.value = f"Exported {len(entries)} passwords to passwords_export.csv"
                status_text.color = ft.Colors.GREEN_400
                page.update()
            except Exception as ex:
                status_text.value = f"Export failed: {ex}"
                status_text.color = ft.Colors.RED_400
                page.update()

        def on_settings_click(e):
            show_settings_popup(page, master_password_session, cipher_suite, update_count)

        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FOREST, size=40, color=ft.Colors.BLUE_400),
                    ft.Text("fern", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        icon_color=ft.Colors.WHITE70,
                        on_click=on_settings_click,
                        tooltip="Settings",
                    ),
                ],
                alignment=ft.MainAxisAlignment.START, spacing=15,
            ), padding=20,
        )

        # Form card
        form_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Add New Password", size=20, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                    ft.Container(height=15),
                    ft.Row([site_field, username_field], spacing=15, expand=True),
                    ft.Container(height=10),
                    ft.Row([password_field], spacing=15, expand=True),
                    strength_bar,
                    ft.Container(height=15),
                    ft.Row(
                        [
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add")], spacing=5), on_click=on_add_click, height=40),
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, size=18), ft.Text("Generate")], spacing=5), on_click=on_generate_click, height=40),
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.SEARCH, size=18), ft.Text("Search")], spacing=5), on_click=on_search_click, height=40),
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.EDIT, size=18), ft.Text("Update")], spacing=5), on_click=on_update_click, height=40),
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.DELETE, size=18), ft.Text("Delete")], spacing=5), on_click=on_delete_click, height=40, bgcolor=ft.Colors.RED_700),
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, size=18), ft.Text("Export")], spacing=5), on_click=on_export_click, height=40),
                        ], spacing=10, wrap=True,
                    ),
                    ft.Container(height=15),
                    status_text,
                ], spacing=0,
            ), padding=25, border_radius=10, bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        )

        # Info section
        info_section = ft.Container(
            content=ft.Row(
                [ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.WHITE54),
                 ft.Text("Passwords are encrypted using Fernet (AES) symmetric encryption.", size=12, color=ft.Colors.WHITE54)],
                spacing=10,
            ), padding=15,
        )

        # Initial count
        update_count()

        # Clear and add main view
        page.controls.clear()
        page.add(
            ft.Column(
                [header, ft.Container(height=10), form_card, ft.Container(height=10), count_text,
                 ft.Container(expand=True), info_section],
                spacing=0, scroll=ft.ScrollMode.AUTO,
            )
        )

    # Start with login view
    show_login_view()


if __name__ == "__main__":
    init_db()
    print("Initializing database...")
    print("Starting fern...")
    ft.app(target=main)