# src/nexusware/screens/auth/login.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from ..base import BaseScreen


class LoginScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.username_input = None
        self.password_input = None
        self.two_factor_input = None
        self.enable_2fa = False
        self.setup_login_form()

    def setup_login_form(self):
        form_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=20,
            alignment='center',
            width=300
        ))

        # Title
        title = toga.Label(
            'Login',
            style=Pack(
                font_size=24,
                font_weight='bold',
                padding=(0, 0, 20, 0)
            )
        )
        form_box.add(title)

        # Username input
        self.username_input = toga.TextInput(
            placeholder='Username',
            style=Pack(
                padding=(0, 0, 10, 0),
                width=250
            )
        )
        form_box.add(self.username_input)

        # Password input
        self.password_input = toga.TextInput(
            placeholder='Password',
            password=True,
            style=Pack(
                padding=(0, 0, 10, 0),
                width=250
            )
        )
        form_box.add(self.password_input)

        # 2FA input (initially hidden)
        self.two_factor_input = toga.TextInput(
            placeholder='2FA Code',
            style=Pack(
                padding=(0, 0, 10, 0),
                width=250,
                display='none'
            )
        )
        form_box.add(self.two_factor_input)

        # Login button
        login_btn = toga.Button(
            'Login',
            on_press=self.handle_login,
            style=Pack(
                padding=10,
                width=250,
                background_color=self.theme['button_background'],
                color=self.theme['button_text']
            )
        )
        form_box.add(login_btn)

        # Error message box
        self.error_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                padding=(10, 0),
                display='none'
            )
        )
        self.error_label = toga.Label(
            '',
            style=Pack(
                color=self.theme['error'],
                font_size=12
            )
        )
        self.error_box.add(self.error_label)
        form_box.add(self.error_box)

        self.content.add(form_box)

    async def handle_login(self, widget):
        try:
            self.hide_error()
            username = self.username_input.value
            password = self.password_input.value

            if not username or not password:
                self.show_form_error("Username and password are required")
                return

            if self.enable_2fa:
                two_factor_code = self.two_factor_input.value
                if not two_factor_code:
                    self.show_form_error("2FA code is required")
                    return

                # Use users_api for 2FA login
                token = await self.window.app.users_api.login_2fa(
                    username=username,
                    password=password,
                    two_factor_code=two_factor_code
                )
            else:
                # Use users_api for regular login
                token = await self.window.app.users_api.login(
                    username=username,
                    password=password
                )

                if getattr(token, 'two_factor_required', False):
                    self.enable_2fa = True
                    self.two_factor_input.style.update(display='flex')
                    self.show_form_error("Please enter your 2FA code")
                    return

            # Store token in cache
            self.cache.set('auth_token', {
                'access_token': token.access_token,
                'refresh_token': token.refresh_token,
                'expires_in': token.expires_in
            })

            # Successfully logged in
            self.window.app.is_authenticated = True
            self.window.app.navigate_to('inventory')

        except Exception as e:
            self.show_form_error(str(e))

    def show_form_error(self, message):
        self.error_label.text = message
        self.error_box.style.update(display='flex')

    def hide_error(self):
        self.error_box.style.update(display='none')
        self.error_label.text = ''
