"""
Main application entry point with single-window login/main view switching.
"""
import flet as ft
from src.database import init_db
from src.security.auth import verify_master_password, hash_master_password
from src.security.encryption import get_salt
from src.database.repository import (
    add_password, get_all_passwords, get_password,
    update_password as repo_update_password,
    delete_password as repo_delete_password,
    get_entry_count
)
from src.security.encryption import get_cipher_suite, encrypt_password, decrypt_password, needs_migration, migrateEncryption, _replace_or_append_env_var
from src.paths import ENV_FILE
from src.utils.password_gen import generate_password
from src.utils.password_strength import check_password_strength
from src.gui.popups import show_delete_popup, show_update_popup, show_search_popup, show_settings_popup

# Module-level idle timer tracking
idle_timer = None  # Track idle timer to prevent leaks

# Page transition overlay
def _fade_transition(page: ft.Page, target_view_fn):
    """Fade to dark → switch view → fade in using on_animation_end chaining."""
    import asyncio

    def on_fade_in_done(e):
        """Overlay is now fully opaque — switch the view underneath."""
        if e.data != "opacity":
            return
        target_view_fn()
        # Now fade the overlay back out
        overlay.on_animation_end = on_fade_out_done
        overlay.opacity = 0
        page.update()

    def on_fade_out_done(e):
        """Overlay is now fully transparent — remove it."""
        if e.data != "opacity":
            return
        if overlay in page.overlay:
            page.overlay.remove(overlay)
            page.update()

    overlay = ft.Container(
        left=0, top=0, right=0, bottom=0,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        opacity=0,
        animate_opacity=300,
        on_animation_end=on_fade_in_done,
    )
    page.overlay.append(overlay)
    page.update()

    # Kick off fade-in after the initial opacity=0 frame renders
    async def start_fade():
        await asyncio.sleep(0.05)
        overlay.opacity = 1
        page.update()

    page.run_task(start_fade)


def is_master_password_set() -> bool:
    """Check if master password has been set (KEY exists in .env)."""
    import os
    return os.getenv("KEY") is not None


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
    last_activity = {"value": None}  # Track last activity timestamp
    IDLE_TIMEOUT = 180  # 3 minutes in seconds

    def record_activity(e=None):
        """Record last activity time."""
        import time
        last_activity["value"] = time.time()

    def show_setup_view():
        """Show first-time setup wizard for creating master password."""
        global idle_timer
        is_logged_in["value"] = False
        master_password_session["value"] = ""
        last_activity["value"] = None  # Reset idle tracking

        # Cancel any existing timer when logging out
        if idle_timer is not None:
            idle_timer.cancel()
            idle_timer = None

        error_message = ft.Text("", color=ft.Colors.ERROR, visible=False)
        success_message = ft.Text("", color=ft.Colors.GREEN_400, visible=False)

        password_field = ft.TextField(
            label="Create Master Password",
            password=True,
            can_reveal_password=True,
            text_size=16,
        )
        confirm_field = ft.TextField(
            label="Confirm Master Password",
            password=True,
            can_reveal_password=True,
            text_size=16,
        )

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

        password_field.on_change = on_password_change

        def on_setup_click(e):
            password = password_field.value
            confirm = confirm_field.value

            if not password or not confirm:
                error_message.value = "Please fill in both fields"
                error_message.visible = True
                success_message.visible = False
                page.update()
                return

            if password != confirm:
                error_message.value = "Passwords do not match"
                error_message.visible = True
                success_message.visible = False
                page.update()
                return

            strength = check_password_strength(password)
            if strength["score"] < 0.3:
                error_message.value = "Password is too weak. Use a stronger password."
                error_message.visible = True
                success_message.visible = False
                page.update()
                return

            # Save hashed password to .env
            password_hash = hash_master_password(password)
            _replace_or_append_env_var("KEY", password_hash)
            # Ensure salt exists
            get_salt()

            is_logged_in["value"] = True
            master_password_session["value"] = password
            success_message.value = "Password created! Setting up..."
            success_message.visible = True
            error_message.visible = False
            page.update()

            import time
            time.sleep(0.5)
            show_main_view()

        confirm_field.on_submit = on_setup_click

        fern_icon = ft.Icon(ft.Icons.FOREST, size=80, color=ft.Colors.BLUE_400)

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        fern_icon,
                        ft.Text("fern", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("First-time setup", size=14, color=ft.Colors.WHITE54),
                        ft.Container(height=20),
                        password_field,
                        strength_bar,
                        ft.Container(height=10),
                        confirm_field,
                        error_message,
                        success_message,
                        ft.Container(height=10),
                        ft.Button(
                            content=ft.Row(
                                [ft.Icon(ft.Icons.FOREST, size=20), ft.Text("Create Password")],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            width=220,
                            height=45,
                            on_click=on_setup_click,
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

    def show_login_view():
        """Show the login view."""
        global idle_timer
        is_logged_in["value"] = False
        master_password_session["value"] = ""
        last_activity["value"] = None  # Reset idle tracking

        # Cancel any existing timer when logging out
        if idle_timer is not None:
            idle_timer.cancel()
            idle_timer = None

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
                _fade_transition(page, show_main_view)
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
                        ft.Button(
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
        global idle_timer
        is_logged_in["value"] = True

        # Cancel any existing timer before creating a new one
        if idle_timer is not None:
            idle_timer.cancel()
            idle_timer = None

        # Record initial activity
        record_activity()

        # Set up repeating idle timer to check every 10 seconds
        def check_idle():
            global idle_timer
            if last_activity["value"] is None:
                return
            import time
            if time.time() - last_activity["value"] > IDLE_TIMEOUT:
                # Auto-lock: return to login
                show_login_view()
                return
            # Reschedule timer for next check
            idle_timer = threading.Timer(10, check_idle)
            idle_timer.daemon = True
            idle_timer.start()

        import threading
        idle_timer = threading.Timer(10, check_idle)
        idle_timer.daemon = True
        idle_timer.start()

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
            record_activity(e)
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
        notes_field = ft.TextField(
            label="Notes (optional)",
            text_size=14,
            expand=1,
        )

        # Password count display
        count_text = ft.Text("", size=14, color=ft.Colors.WHITE70)

        def update_count():
            count = get_entry_count()
            count_text.value = f"Total passwords stored: {count}"
            page.update()

        def on_add_click(e):
            record_activity()
            site = site_field.value.strip()
            username = username_field.value.strip()
            password = password_field.value
            notes = notes_field.value.strip() if notes_field.value else None

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
            add_password(site, username, encrypted, notes)

            site_field.value = ""
            username_field.value = ""
            password_field.value = ""
            notes_field.value = ""
            strength_bar.visible = False
            status_text.value = f"Password for '{site}' added successfully!"
            status_text.color = ft.Colors.GREEN_400
            update_count()
            page.update()

        def on_generate_click(e):
            record_activity()
            generated = generate_password()
            password_field.value = generated
            on_password_change(None)
            status_text.value = "Password generated!"
            status_text.color = ft.Colors.BLUE_400
            page.update()

        def on_search_click(e):
            record_activity()
            show_search_popup(page, cipher_suite)

        def on_update_click(e):
            record_activity()
            show_update_popup(page, cipher_suite, update_count)

        def on_delete_click(e):
            record_activity()
            show_delete_popup(page, update_count)

        def on_export_click(e):
            record_activity()
            import csv
            import os
            from src.paths import EXPORT_DIR
            try:
                entries = get_all_passwords()
                if not entries:
                    status_text.value = "No passwords to export"
                    status_text.color = ft.Colors.ORANGE_400
                    page.update()
                    return

                export_path = os.path.join(EXPORT_DIR, "passwords_export.csv")

                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Site", "Username", "Password", "Notes"])
                    for entry in entries:
                        try:
                            decrypted = decrypt_password(entry.password, cipher_suite)
                        except:
                            decrypted = "***"
                        writer.writerow([entry.site, entry.user, decrypted, entry.notes or ""])

                status_text.value = f"Exported {len(entries)} passwords to passwords_export.csv"
                status_text.color = ft.Colors.GREEN_400
                page.update()
            except Exception as ex:
                status_text.value = f"Export failed: {ex}"
                status_text.color = ft.Colors.RED_400
                page.update()

        def on_settings_click(e):
            record_activity()
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
                    ft.Container(height=10),
                    ft.Row([notes_field], spacing=15, expand=True),
                    ft.Container(height=15),
                    ft.Row(
                        [
                            ft.Button(content=ft.Row([ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add")], spacing=5), on_click=on_add_click, height=40),
                            ft.Button(content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, size=18), ft.Text("Generate")], spacing=5), on_click=on_generate_click, height=40),
                            ft.Button(content=ft.Row([ft.Icon(ft.Icons.SEARCH, size=18), ft.Text("Search")], spacing=5), on_click=on_search_click, height=40),
                            ft.Button(content=ft.Row([ft.Icon(ft.Icons.EDIT, size=18), ft.Text("Update")], spacing=5), on_click=on_update_click, height=40),
                            ft.Button(content=ft.Row([ft.Icon(ft.Icons.DELETE, size=18), ft.Text("Delete")], spacing=5), on_click=on_delete_click, height=40, bgcolor=ft.Colors.RED_700),
                            ft.Button(content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, size=18), ft.Text("Export")], spacing=5), on_click=on_export_click, height=40),
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

        # Hook into page events for activity tracking
        def on_mouse_move(e):
            record_activity()
        page.on_mouse_move = on_mouse_move

        # Clear and add main view
        page.controls.clear()
        page.add(
            ft.Column(
                [header, ft.Container(height=10), form_card, ft.Container(height=10), count_text,
                 ft.Container(expand=True), info_section],
                spacing=0, scroll=ft.ScrollMode.AUTO,
            )
        )

    # Start with setup view if first time, otherwise login
    if is_master_password_set():
        show_login_view()
    else:
        show_setup_view()


if __name__ == "__main__":
    init_db()
    print("Initializing database...")
    print("Starting fern...")
    ft.app(target=main)