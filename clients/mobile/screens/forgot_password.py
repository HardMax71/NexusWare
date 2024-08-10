# /clients/mobile/screens/forgot_password.py

import flet as ft
from flet import (
    Column,
    Container,
    Text,
    TextField,
    ElevatedButton,
    TextButton,
    Image,
    ProgressBar,
    colors,
)


class ForgotPasswordScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.email_field = TextField(
            label="Email",
            border=ft.InputBorder.OUTLINE,
            width=300,
            height=56,
        )
        self.reset_button = ElevatedButton(
            text="Reset Password",
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
        self.back_to_login_button = TextButton(
            text="Back to Login",
            style=ft.ButtonStyle(
                color={
                    ft.MaterialState.HOVERED: colors.BLUE_700,
                    ft.MaterialState.DEFAULT: colors.BLUE_600,
                },
            ),
        )
        self.message_text = Text(
            size=14,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        self.progress_bar = ProgressBar(visible=False, width=300)

    def build(self):
        return Container(
            width=self.app.page.width,
            height=self.app.page.height,
            image_src="/assets/logo.png",
            image_fit=ft.ImageFit.COVER,
            content=Container(
                width=self.app.page.width,
                height=self.app.page.height,
                bgcolor=ft.colors.with_opacity(0.9, ft.colors.WHITE),
                content=Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        Image(
                            src="/assets/logo.png",
                            width=200,
                            height=200,
                        ),
                        Container(height=20),
                        Text(
                            "Forgot Password",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=colors.BLUE_600,
                        ),
                        Container(height=10),
                        Text(
                            "Enter your email address to reset your password.",
                            size=16,
                            color=colors.GREY_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        Container(height=20),
                        self.email_field,
                        Container(height=10),
                        self.message_text,
                        Container(height=10),
                        self.progress_bar,
                        Container(height=20),
                        self.reset_button,
                        Container(height=10),
                        self.back_to_login_button,
                    ],
                ),
            ),
        )

    def did_mount(self):
        self.reset_button.on_click = self.reset_password
        self.back_to_login_button.on_click = self.back_to_login

    async def reset_password(self, e):
        self.message_text.value = ""
        email = self.email_field.value

        if not email:
            self.message_text.value = "Please enter your email address."
            self.message_text.color = colors.RED_600
            self.update()
            return

        self.reset_button.disabled = True
        self.progress_bar.visible = True
        self.update()

        try:
            response = await self.app.client.post("/users/reset-password",
                                                  json={"email": email},
                                                  timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.message_text.value = result["message"]
                self.message_text.color = colors.GREEN_600
            elif response.status_code == 404:
                self.message_text.value = "The email address is not registered in our system."
                self.message_text.color = colors.RED_600
            else:
                self.message_text.value = "An error occurred. Please try again later."
                self.message_text.color = colors.RED_600
        except Exception as ex:
            self.message_text.value = f"An error occurred: {str(ex)}"
            self.message_text.color = colors.RED_600

        self.reset_button.disabled = False
        self.progress_bar.visible = False
        self.update()

    def back_to_login(self, e):
        self.app.page.go("/login")
