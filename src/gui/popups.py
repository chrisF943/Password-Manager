import flet as ft
import pyperclip
from src.database.repository import get_all_passwords, delete_password, update_password
from src.security.encryption import decrypt_password, encrypt_password
from src.security.auth import hash_master_password


def show_delete_popup(page: ft.Page, on_delete_callback):
    """Show dialog with list of sites to delete."""

    # Store selected site
    selected_site = {"site": None}

    # Container for the list
    list_container = ft.ListView(
        expand=True,
        spacing=5,
        padding=10,
    )

    def load_entries():
        list_container.controls.clear()
        entries = get_all_passwords()
        for entry in entries:
            list_container.controls.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(entry.site),
                        subtitle=ft.Text(entry.user),
                        leading=ft.Icon(ft.Icons.LINK, size=20),
                        on_click=lambda e, site=entry.site: select_entry(site),
                    ),
                    border_radius=5,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    padding=5,
                )
            )
        page.update()

    def select_entry(site):
        selected_site["site"] = site
        # Highlight selected
        for i, ctrl in enumerate(list_container.controls):
            if isinstance(ctrl, ft.Container):
                tile = ctrl.content
                if tile.title.value == site:
                    ctrl.bgcolor = ft.Colors.PRIMARY_CONTAINER
                else:
                    ctrl.bgcolor = ft.Colors.SURFACE_CONTAINER_LOW
        page.update()

    # Load initial data
    load_entries()

    def delete_selected(e):
        if not selected_site["site"]:
            main_dlg.open = False
            page.update()
            # Show warning dialog instead of snackbar
            warning_dlg = ft.AlertDialog(
                title=ft.Text("Warning"),
                content=ft.Text("Please select an entry to delete."),
                actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_warning(warning_dlg))],
            )
            def close_warning(dlg):
                dlg.open = False
                page.update()
            page.show_dialog(warning_dlg)
            return

        site = selected_site["site"]

        # Show confirmation dialog
        def confirm_delete(e2):
            delete_password(site)
            selected_site["site"] = None
            load_entries()
            on_delete_callback()
            confirm_dlg.open = False
            main_dlg.open = False
            page.update()
            # Show success dialog
            success_dlg = ft.AlertDialog(
                title=ft.Text("Deleted"),
                content=ft.Text(f"Entry for '{site}' deleted."),
                actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_success(success_dlg))],
            )
            def close_success(dlg):
                dlg.open = False
                page.update()
            page.show_dialog(success_dlg)

        confirm_dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete '{site}'?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=lambda e: setattr(confirm_dlg, 'open', False) or page.update()),
                ft.TextButton(content=ft.Text("Delete"), on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(confirm_dlg)

    def close_popup(e):
        main_dlg.open = False

    # Create the main dialog
    main_dlg = ft.AlertDialog(
        title=ft.Text("Delete Password Entry"),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Select an entry to delete:"),
                ft.Container(
                    content=list_container,
                    height=250,
                    width=400,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=5,
                ),
            ], tight=True),
            width=450,
            height=350,
        ),
        actions=[
            ft.TextButton(content=ft.Text("Delete"), on_click=delete_selected),
            ft.TextButton(content=ft.Text("Close"), on_click=close_popup),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(main_dlg)


def show_update_popup(page: ft.Page, cipher_suite, on_update_callback):
    """Show dialog with list of entries to update."""

    # Store selected entry
    selected_site = {"site": None}

    # Container for the list
    list_container = ft.ListView(
        expand=True,
        spacing=5,
        padding=10,
    )

    def load_entries():
        list_container.controls.clear()
        entries = get_all_passwords()
        for entry in entries:
            # Decrypt password for display (masked)
            try:
                decrypted = decrypt_password(entry.password, cipher_suite)
                masked = "*" * len(decrypted)
            except:
                masked = "***"

            list_container.controls.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(str(entry.site)),
                        subtitle=ft.Text(f"{entry.user} | {masked}"),
                        leading=ft.Icon(ft.Icons.LINK, size=20),
                        on_click=lambda e, site=entry.site: select_entry(site),
                    ),
                    border_radius=5,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    padding=5,
                )
            )
        page.update()

    def select_entry(site):
        selected_site["site"] = site
        # Highlight selected
        for ctrl in list_container.controls:
            if isinstance(ctrl, ft.Container):
                tile = ctrl.content
                if tile.title.value == site:
                    ctrl.bgcolor = ft.Colors.PRIMARY_CONTAINER
                else:
                    ctrl.bgcolor = ft.Colors.SURFACE_CONTAINER_LOW
        page.update()

    # Load initial data
    load_entries()

    def open_edit_dialog(e):
        if not selected_site["site"]:
            main_dlg.open = False
            page.update()
            # Show warning dialog instead of snackbar
            warning_dlg = ft.AlertDialog(
                title=ft.Text("Warning"),
                content=ft.Text("Please select an entry to edit."),
                actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_warning(warning_dlg))],
            )
            def close_warning(dlg):
                dlg.open = False
                page.update()
            page.show_dialog(warning_dlg)
            return

        site = selected_site["site"]

        # Get actual entry data
        entries = get_all_passwords()
        entry = next((e for e in entries if e.site == site), None)
        if not entry:
            return

        try:
            actual_password = decrypt_password(entry.password, cipher_suite)
        except:
            actual_password = ""

        # Edit fields
        username_field = ft.TextField(label="Username", value=entry.user)
        password_field = ft.TextField(
            label="Password",
            value=actual_password,
            password=True,
            can_reveal_password=True
        )

        def save_changes(e2):
            new_username = username_field.value
            new_password = password_field.value

            if not new_username or not new_password:
                # Show error dialog
                error_dlg = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text("All fields are required."),
                    actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_error(error_dlg))],
                )
                def close_error(dlg):
                    dlg.open = False
                    page.update()
                page.show_dialog(error_dlg)
                return

            # Encrypt and update
            encrypted = encrypt_password(new_password, cipher_suite)
            update_password(site, encrypted, new_username)

            edit_dlg.open = False
            main_dlg.open = False
            page.update()
            # Show success dialog
            success_dlg = ft.AlertDialog(
                title=ft.Text("Success"),
                content=ft.Text("Entry updated successfully."),
                actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_success(success_dlg))],
            )
            def close_success(dlg):
                dlg.open = False
                page.update()
            page.show_dialog(success_dlg)

        edit_dlg = ft.AlertDialog(
            title=ft.Text(f"Edit: {site}"),
            content=ft.Container(
                content=ft.Column([
                    ft.TextField(label="Website", value=site, read_only=True),
                    username_field,
                    password_field,
                ], tight=True),
                width=350,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=lambda e: setattr(edit_dlg, 'open', False) or page.update()),
                ft.TextButton(content=ft.Text("Save"), on_click=save_changes),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(edit_dlg)

    def close_popup(e):
        main_dlg.open = False

    # Create the main dialog
    main_dlg = ft.AlertDialog(
        title=ft.Text("Update Password Entry"),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Select an entry to edit:"),
                ft.Container(
                    content=list_container,
                    height=250,
                    width=450,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=5,
                ),
            ], tight=True),
            width=500,
            height=350,
        ),
        actions=[
            ft.TextButton(content=ft.Text("Edit Selected"), on_click=open_edit_dialog),
            ft.TextButton(content=ft.Text("Close"), on_click=close_popup),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(main_dlg)


def show_search_popup(page: ft.Page, cipher_suite):
    """Show dialog with searchable list of entries."""

    all_entries = []
    filtered_entries = []

    search_field = ft.TextField(
        label="Search",
        hint_text="Type to filter by website...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: filter_entries()
    )

    # Container for the list
    list_container = ft.ListView(
        expand=True,
        spacing=5,
        padding=10,
    )

    def load_entries():
        list_container.controls.clear()
        filter_text = search_field.value.lower() if search_field.value else ""

        for entry in filtered_entries:
            if filter_text and filter_text not in str(entry.site).lower():
                continue
            # Decrypt password for display (masked)
            try:
                decrypted = decrypt_password(entry.password, cipher_suite)
                masked = "*" * len(decrypted)
            except:
                masked = "***"

            list_container.controls.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(str(entry.site)),
                        subtitle=ft.Text(f"{entry.user} | {masked}"),
                        leading=ft.Icon(ft.Icons.LINK, size=20),
                        on_click=lambda e, site=entry.site, pwd=decrypted: copy_password(site, pwd),
                    ),
                    border_radius=5,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    padding=5,
                )
            )
        page.update()

    def filter_entries():
        load_entries()

    # Load initial data
    all_entries = get_all_passwords()
    filtered_entries = all_entries
    load_entries()

    selected_site = {"site": None, "password": None}

    def copy_password(site, password):
        try:
            pyperclip.copy(password)
            main_dlg.open = False
            page.update()
            # Show confirmation dialog
            confirm_dlg = ft.AlertDialog(
                title=ft.Text("Copied!"),
                content=ft.Text(f"Password for '{site}' copied to clipboard."),
                actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_confirm(confirm_dlg))],
            )
            def close_confirm(dlg):
                dlg.open = False
                page.update()
            page.show_dialog(confirm_dlg)
        except Exception as ex:
            main_dlg.open = False
            page.update()
            error_dlg = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"Failed to copy: {ex}"),
                actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_error(error_dlg))],
            )
            def close_error(dlg):
                dlg.open = False
                page.update()
            page.show_dialog(error_dlg)

    def close_popup(e):
        main_dlg.open = False

    # Create the main dialog
    main_dlg = ft.AlertDialog(
        title=ft.Text("Search Passwords"),
        content=ft.Container(
            content=ft.Column([
                search_field,
                ft.Container(
                    content=list_container,
                    height=250,
                    width=450,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=5,
                ),
            ], tight=True),
            width=500,
            height=380,
        ),
        actions=[
            ft.TextButton(content=ft.Text("Close"), on_click=close_popup),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(main_dlg)


def show_settings_popup(page: ft.Page, master_password_session: dict, current_cipher, on_update_callback):
    """Show settings dialog for changing master password."""

    current_password_field = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        text_size=14,
        expand=1,
    )
    new_password_field = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        text_size=14,
        expand=1,
    )
    confirm_password_field = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        text_size=14,
        expand=1,
    )

    # Strength indicator for new password
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

    def on_new_password_change(e):
        password = new_password_field.value
        if not password:
            strength_bar.visible = False
        else:
            from src.utils.password_strength import check_password_strength
            strength = check_password_strength(password)
            strength_bar.visible = True
            bar = strength_bar.content.controls[0]
            bar.content.width = int(strength["score"] * 25)
            bar.content.bgcolor = strength["color"]
            strength_text.value = strength["message"]
            strength_text.color = strength["color"]
        page.update()

    new_password_field.on_change = on_new_password_change

    status_text = ft.Text("", size=13, color=ft.Colors.RED_400, visible=False)

    def change_password(e):
        status_text.visible = True
        current_pw = current_password_field.value
        new_pw = new_password_field.value
        confirm_pw = confirm_password_field.value

        # Validate current password
        from src.security.auth import verify_master_password
        if not verify_master_password(current_pw):
            status_text.value = "Current password is incorrect."
            page.update()
            return

        # Validate new passwords match
        if new_pw != confirm_pw:
            status_text.value = "New passwords do not match."
            status_text.color = ft.Colors.RED_400
            page.update()
            return

        # Validate new password is not empty
        if not new_pw:
            status_text.value = "New password cannot be empty."
            status_text.color = ft.Colors.RED_400
            page.update()
            return

        # Validate password strength
        from src.utils.password_strength import check_password_strength
        strength = check_password_strength(new_pw)
        if strength["score"] < 0.3:
            status_text.value = "New password is too weak. Use a stronger password."
            status_text.color = ft.Colors.RED_400
            page.update()
            return

        # Re-encrypt all passwords
        from src.security.encryption import (
            get_cipher_suite, encrypt_password, decrypt_password
        )
        from src.database.repository import get_all_passwords, update_password

        old_cipher = current_cipher
        new_cipher = get_cipher_suite(new_pw)

        entries = get_all_passwords()
        success = 0
        errors = 0
        for entry in entries:
            try:
                decrypted = decrypt_password(entry.password, old_cipher)
                new_encrypted = encrypt_password(decrypted, new_cipher)
                update_password(entry.site, new_encrypted, entry.user)
                success += 1
            except Exception:
                errors += 1

        if errors > 0:
            status_text.value = f"Failed to re-encrypt {errors} entries. Password NOT changed."
            status_text.color = ft.Colors.RED_400
            page.update()
            return

        # Update .env with new password (use absolute path)
        import os
        from src.paths import ENV_FILE

        # Read current .env
        lines = []
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r") as f:
                lines = f.readlines()

        # Replace KEY line (or append if not present) — store HASH, not plaintext
        key_found = False
        new_lines = []
        new_hash = hash_master_password(new_pw)
        for line in lines:
            if line.startswith("KEY="):
                new_lines.append(f"KEY={new_hash}\n")
                key_found = True
            else:
                new_lines.append(line)
        if not key_found:
            new_lines.append(f"KEY={new_hash}\n")

        with open(ENV_FILE, "w") as f:
            f.writelines(new_lines)

        # Update session password so subsequent operations use new cipher
        master_password_session["value"] = new_pw

        # Notify caller to refresh UI
        if on_update_callback:
            on_update_callback()

        # Success
        settings_dlg.open = False
        page.update()

        success_dlg = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text(f"Master password changed. {success} passwords re-encrypted."),
            actions=[ft.TextButton(content=ft.Text("OK"), on_click=lambda e: close_success(success_dlg))],
        )
        def close_success(dlg):
            dlg.open = False
            page.update()
        page.show_dialog(success_dlg)

    def close_popup(e):
        settings_dlg.open = False
        page.update()

    settings_dlg = ft.AlertDialog(
        title=ft.Text("Settings"),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Change Master Password", size=16, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                ft.Container(height=10),
                current_password_field,
                ft.Container(height=8),
                new_password_field,
                strength_bar,
                ft.Container(height=8),
                confirm_password_field,
                ft.Container(height=5),
                status_text,
            ], tight=True),
            width=400,
        ),
        actions=[
            ft.TextButton(content=ft.Text("Cancel"), on_click=close_popup),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.CHECK, size=16), ft.Text("Change Password")], spacing=5),
                on_click=change_password,
                height=38,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(settings_dlg)
