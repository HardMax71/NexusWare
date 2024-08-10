import flet as ft
from flet import (
    Column,
    Container,
    Text,
    TextField,
    ElevatedButton,
    TextButton,
    Image,
    colors,
)


class LoginScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.email_field = TextField(
            label="Email",
            border=ft.InputBorder.OUTLINE,
            width=300,
            height=56,
        )
        self.password_field = TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.OUTLINE,
            width=300,
            height=56,
        )
        self.login_button = ElevatedButton(
            text="Login",
            width=300,
            height=48,
            style=ft.ButtonStyle(
                color={
                    ft.MaterialState.HOVERED: colors.WHITE,
                    ft.MaterialState.DEFAULT: colors.WHITE,
                },
                bgcolor={
                    ft.MaterialState.HOVERED: colors.BLUE_700,
                    ft.MaterialState.DEFAULT: colors.BLUE_600,
                },
            ),
        )
        self.forgot_password_button = TextButton(
            text="Forgot Password?",
            style=ft.ButtonStyle(
                color={
                    ft.MaterialState.HOVERED: colors.BLUE_700,
                    ft.MaterialState.DEFAULT: colors.BLUE_600,
                },
            ),
        )
        self.error_text = Text(
            color=colors.RED_600,
            size=14,
            weight=ft.FontWeight.BOLD,
        )

    def build(self):
        return Container(
            width=self.app.page.width,
            height=self.app.page.height,
            bgcolor=ft.colors.WHITE,
            content=Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    Image(
                        src="logo.png",
                        width=200,
                        height=200,
                    ),
                    Container(height=20),
                    Container(
                        width=300,
                        padding=ft.padding.all(20),
                        content=Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.email_field,
                                Container(height=10),
                                self.password_field,
                                Container(height=10),
                                self.error_text,
                                Container(height=20),
                                self.login_button,
                                Container(height=10),
                                self.forgot_password_button,
                            ],
                        ),
                    ),
                ],
            ),
        )

    def did_mount(self):
        self.login_button.on_click = self.login
        self.forgot_password_button.on_click = self.forgot_password

    async def login(self, e):
        self.error_text.value = ""
        email = self.email_field.value
        password = self.password_field.value

        if not email or not password:
            self.error_text.value = "Please enter both email and password."
            self.update()
            return

        self.login_button.disabled = True
        self.update()

        success = await self.app.login(email, password)

        if success:
            self.app.page.go("/")
        else:
            self.error_text.value = "Invalid email or password."
            self.login_button.disabled = False
            self.update()

    def forgot_password(self, e):
        self.app.page.go("/forgot-password")
