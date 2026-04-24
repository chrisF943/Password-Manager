"""
Login Page - Flet-based login screen for fern.
"""
import flet as ft
from src.security.auth import verify_master_password


def show_login():
    """Display the login window. On success, launches main window."""

    def login_page(page: ft.Page):
        page.title = "fern - Login"
        page.theme_mode = ft.ThemeMode.DARK
        page.window.width = 400
        page.window.height = 380
        page.window.resizable = False

        # Import main_page here to avoid circular imports
        from src.gui.main_page import main_page

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
                # Close window and open main in a new window
                page.window_destroy()
                main_page(page)
            else:
                error_message.value = "Incorrect password"
                error_message.visible = True
                password_field.value = ""
                page.update()

        password_field.on_submit = on_login_click

        fern_icon = ft.Icon(
            ft.Icons.FOREST,
            size=80,
            color=ft.Colors.BLUE_400,
        )

        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        fern_icon,
                        ft.Text(
                            "fern",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(
                            "Enter your master password",
                            size=14,
                            color=ft.Colors.WHITE54,
                        ),
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

    ft.app(target=login_page)


if __name__ == "__main__":
    show_login()
