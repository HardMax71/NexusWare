import flet as ft
from utils.validators import validate_email, validate_password
from utils.api_helper import api_call

class LoginScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.email = ft.TextField(
            label="Email",
            width=300,
            autofocus=True,
        )
        self.password = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        self.login_button = ft.ElevatedButton("Login", on_click=self.login)
        self.forgot_password_button = ft.TextButton("Forgot Password?", on_click=self.show_forgot_password)
        self.error_text = ft.Text("", color=ft.colors.RED)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Image(src="/assets/logo.png", width=200, height=200),
                    self.email,
                    self.password,
                    self.login_button,
                    self.forgot_password_button,
                    self.error_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            padding=40,
            width=400,
            height=600,
        )

    async def login(self, _):
        await self.do_login()

    async def do_login(self):
        self.error_text.value = ""
        self.login_button.disabled = True
        await self.update_async()

        # Validate email
        if not validate_email(self.email.value):
            self.error_text.value = "Invalid email format"
            self.login_button.disabled = False
            await self.update_async()
            return

        # Prepare login data
        login_data = {
            "username": self.email.value,
            "password": self.password.value
        }

        try:
            # API call for login
            response = await api_call(self.app, self.app.client.post, "/users/login", data=login_data)
            if response and "access_token" in response:
                self.app.token = response["access_token"]
                self.app.client.headers["Authorization"] = f"Bearer {self.app.token}"
                await self.app.load_user_data()
                await self.app.page.go_async("/")
            else:
                self.error_text.value = "Invalid email or password"
        except Exception as e:
            self.error_text.value = f"An error occurred: {str(e)}"

        # Re-enable the button and update UI
        self.login_button.disabled = False
        await self.update_async()

    def show_forgot_password(self, _):
        self.app.page.go("/forgot-password")

    def did_mount(self):
        pass

    def will_unmount(self):
        pass
