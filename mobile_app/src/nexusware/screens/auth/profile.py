# src/nexusware/screens/auth/profile.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..base import BaseScreen
from public_api.shared_schemas import UserUpdate


class ProfileScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.setup_profile()

    async def setup_profile(self):
        self.user_data = await self.window.app.users_api.get_current_user()

        profile_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=20
        ))

        # Header
        header = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 20, 0)
        ))

        title = toga.Label(
            'Profile',
            style=Pack(
                font_size=24,
                font_weight='bold'
            )
        )
        header.add(title)

        edit_btn = toga.Button(
            'Edit',
            on_press=self.handle_edit,
            style=Pack(
                padding=(0, 0, 0, 10),
                background_color=self.theme['button_background'],
                color=self.theme['button_text']
            )
        )
        header.add(edit_btn)

        profile_box.add(header)

        # User info
        fields = [
            ('Username', self.user_data.username),
            ('Email', self.user_data.email),
            ('Role', self.user_data.role.name),
            ('2FA Enabled', 'Yes' if self.user_data.two_factor_auth_enabled else 'No'),
            ('Last Login', self.format_timestamp(self.user_data.last_login)),
            ('Account Created', self.format_timestamp(self.user_data.created_at))
        ]

        for label, value in fields:
            field_box = toga.Box(style=Pack(
                direction=ROW,
                padding=(0, 0, 10, 0)
            ))

            label_widget = toga.Label(
                f'{label}:',
                style=Pack(
                    font_weight='bold',
                    padding=(0, 10, 0, 0),
                    width=150
                )
            )
            field_box.add(label_widget)

            value_widget = toga.Label(
                str(value),
                style=Pack(padding=(0, 10, 0, 0))
            )
            field_box.add(value_widget)

            profile_box.add(field_box)

        # Security section
        security_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(20, 0)
        ))

        security_title = toga.Label(
            'Security',
            style=Pack(
                font_size=18,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        security_box.add(security_title)

        change_pass_btn = toga.Button(
            'Change Password',
            on_press=self.handle_change_password,
            style=Pack(
                padding=5,
                width=200,
                background_color=self.theme['button_background'],
                color=self.theme['button_text']
            )
        )
        security_box.add(change_pass_btn)

        toggle_2fa_btn = toga.Button(
            'Disable 2FA' if self.user_data.two_factor_auth_enabled else 'Enable 2FA',
            on_press=self.handle_toggle_2fa,
            style=Pack(
                padding=5,
                width=200,
                background_color=self.theme['button_background'],
                color=self.theme['button_text']
            )
        )
        security_box.add(toggle_2fa_btn)

        profile_box.add(security_box)
        self.content.add(profile_box)

    def format_timestamp(self, timestamp):
        if not timestamp:
            return 'Never'
        return self.format_date(timestamp)

    async def handle_edit(self, widget):
        # Navigate to edit profile screen
        self.window.app.navigate_to('profile/edit')

    async def handle_change_password(self, widget):
        # Show change password dialog
        password_dialog = self.create_password_dialog()
        await self.window.app.dialog(password_dialog)

    async def handle_toggle_2fa(self, widget):
        users_api = self.window.app.users_api
        try:
            if self.user_data.two_factor_auth_enabled:
                # Use appropriate users API method for disabling 2FA
                user_update = UserUpdate(two_factor_auth_enabled=False)
                await users_api.update_current_user(user_update)
                self.show_success("2FA has been disabled")
            else:
                # Get 2FA setup details from users API
                qr_code = await users_api.update_current_user(
                    UserUpdate(two_factor_auth_enabled=True)
                )
                self.show_2fa_setup_dialog(qr_code)

            # Refresh profile data
            await self.setup_profile()

        except Exception as e:
            self.show_error(str(e))

    def create_password_dialog(self):
        dialog = toga.Dialog(
            title='Change Password',
            content=self.create_password_form(),
            on_result=self.handle_password_change
        )
        return dialog

    def create_password_form(self):
        form_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10
        ))

        self.current_password = toga.TextInput(
            placeholder='Current Password',
            password=True,
            style=Pack(padding=5)
        )
        form_box.add(self.current_password)

        self.new_password = toga.TextInput(
            placeholder='New Password',
            password=True,
            style=Pack(padding=5)
        )
        form_box.add(self.new_password)

        self.confirm_password = toga.TextInput(
            placeholder='Confirm New Password',
            password=True,
            style=Pack(padding=5)
        )
        form_box.add(self.confirm_password)

        return form_box

    async def handle_password_change(self, dialog, result):
        if result:
            try:
                if self.new_password.value != self.confirm_password.value:
                    raise ValueError("New passwords don't match")

                await self.window.app.users_api.change_password(
                    self.current_password.value,
                    self.new_password.value
                )

                self.show_success("Password changed successfully")

            except Exception as e:
                self.show_error(str(e))

    def show_2fa_setup_dialog(self, qr_code):
        setup_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10
        ))

        # QR code image
        qr_image = toga.Image(qr_code)
        image_view = toga.ImageView(qr_image)
        setup_box.add(image_view)

        # Instructions
        instructions = toga.Label(
            'Scan this QR code with your authenticator app',
            style=Pack(padding=10)
        )
        setup_box.add(instructions)

        # Verification code input
        self.verification_code = toga.TextInput(
            placeholder='Enter verification code',
            style=Pack(padding=10)
        )
        setup_box.add(self.verification_code)

        dialog = toga.Dialog(
            title='Set up 2FA',
            content=setup_box,
            on_result=self.handle_2fa_verification
        )
        dialog.show()

    async def handle_2fa_verification(self, dialog, result):
        if result:
            try:
                # Use appropriate users API method for 2FA verification
                await self.window.app.users_api.login_2fa(
                    username=self.user_data.username,
                    password="",  # Password not needed for verification
                    two_factor_code=self.verification_code.value
                )
                self.show_success("2FA has been enabled")
                await self.setup_profile()
            except Exception as e:
                self.show_error(str(e))