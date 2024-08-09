# /clients/mobile/screens/forgot_password.py

import flet as ft
from utils.validators import validate_email
from utils.api_helper import api_call

class ForgotPasswordScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.email = ft.TextField(label="Email", width=300)
        self.reset_button = ft.ElevatedButton("Reset Password", on_click=self.reset_password)
        self.back_button = ft.TextButton("Back to Login", on_click=self.back_to_login)
        self.message_text = ft.Text("", color="green")

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Forgot Password", size=24, weight=ft.FontWeight.BOLD),
                    self.email,
                    self.reset_button,
                    self.back_button,
                    self.message_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            padding=20,
        )

    async def reset_password(self, e):
        self.message_text.value = ""
        if not validate_email(self.email.value):
            self.message_text.value = "Invalid email format"
            self.message_text.color = "red"
            self.update()
            return

        reset_data = {
            "email": self.email.value
        }

        response = await api_call(self.app, self.app.client.post, "/users/reset-password", json=reset_data)
        if response:
            self.message_text.value = "Password reset instructions sent to your email"
            self.message_text.color = "green"
        else:
            self.message_text.value = "Error occurred while resetting password"
            self.message_text.color = "red"
        self.update()

    def back_to_login(self, e):
        self.app.page.go("/login")

    def did_mount(self):
        self.email.focus()
