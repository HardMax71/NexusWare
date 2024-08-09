# /clients/mobile/screens/profile.py

import flet as ft


class ProfileScreen(ft.UserControl):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def build(self):
        self.user_avatar = ft.CircleAvatar(foreground_image_url="", radius=50)
        self.user_name = ft.Text("", size=24, weight=ft.FontWeight.BOLD)
        self.user_email = ft.Text("", size=16)

        self.options_list = ft.ListView(
            controls=[
                self.create_option("Account Settings", ft.icons.SETTINGS, self.open_account_settings),
                self.create_option("Notifications", ft.icons.NOTIFICATIONS, self.open_notifications),
                self.create_option("App Settings", ft.icons.PHONE_ANDROID, self.open_app_settings),
                self.create_option("Help & Support", ft.icons.HELP, self.open_help_support),
            ],
            spacing=10,
            padding=20,
        )

        self.logout_button = ft.ElevatedButton("Logout", on_click=self.logout)

        return ft.Column(
            [
                ft.AppBar(title=ft.Text("Profile")),
                ft.Column(
                    [
                        self.user_avatar,
                        self.user_name,
                        self.user_email,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                self.options_list,
                self.logout_button,
                ft.Text("Version 1.0.0", size=12, color=ft.colors.GREY),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    async def load_user_data(self):
        response = await self.app.client.get("/users/me")
        if response.status_code == 200:
            user_data = response.json()
            self.user_avatar.foreground_image_url = user_data.get("avatar_url", "")
            self.user_name.value = user_data.get("name", "")
            self.user_email.value = user_data.get("email", "")
            self.update()

    def create_option(self, title, icon, on_click):
        return ft.ListTile(
            leading=ft.Icon(icon),
            title=ft.Text(title),
            trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS),
            on_click=on_click,
        )

    def open_account_settings(self, e):
        # Implement account settings logic
        pass

    def open_notifications(self, e):
        # Implement notifications settings logic
        pass

    def open_app_settings(self, e):
        # Implement app settings logic
        pass

    def open_help_support(self, e):
        # Implement help & support logic
        pass

    def logout(self, e):
        self.app.logout()
