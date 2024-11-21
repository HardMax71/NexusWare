# src/nexusware/screens/base.py

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from mobile_app.src.nexusware.utils import (CacheManager,
                                            NetworkManager,
                                            ThemeManager)
from public_api.shared_schemas import UserSanitized


class BaseScreen(toga.Window):
    def __init__(self):
        super().__init__()
        self.api_client = self.window.app.api_client
        self.users_api = self.window.app.users_api
        self.theme_manager = ThemeManager()
        self.theme = self.theme_manager.get_theme()
        self.network = NetworkManager()
        self.cache = CacheManager()

        # UI components
        self.main_box = None
        self.header = None
        self.content = None
        self.footer = None
        self.loading_overlay = None
        self.user_data: UserSanitized | None = None

        # Setup UI
        self.setup_ui()
        self.load_user_data()

    async def load_user_data(self):
        """Load current user data"""
        try:
            # Use UsersAPI instead of AuthService
            self.user_data = await self.app.users_api.get_current_user()
            self.update_user_menu()
        except Exception:
            # Handle unauthorized access
            self.window.app.navigate_to('login')

    def setup_ui(self):
        """Initialize the base UI structure"""
        # Main container
        self.main_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10,
            background_color=self.theme['background']
        ))

        # Header
        self.header = self.create_header()
        self.main_box.add(self.header)

        # Content area with loading overlay
        content_container = toga.Box(style=Pack(
            direction=COLUMN,
            flex=1
        ))

        self.content = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10,
            flex=1,
            background_color=self.theme['content_background']
        ))
        content_container.add(self.content)

        # Loading overlay (initially hidden)
        self.loading_overlay = toga.Box(
            style=Pack(
                direction=COLUMN,
                padding=20,
                alignment='center',
                background_color='rgba(255, 255, 255, 0.8)',
                display='none'
            )
        )

        spinner_label = toga.Label(
            '⟳',  # This could be replaced with an actual spinner image
            style=Pack(
                font_size=32,
                font_weight='bold',
                color=self.theme['header_background']
            )
        )
        self.loading_overlay.add(spinner_label)

        loading_text = toga.Label(
            'Loading...',
            style=Pack(
                font_size=14,
                color=self.theme['header_background']
            )
        )
        self.loading_overlay.add(loading_text)

        content_container.add(self.loading_overlay)

        self.main_box.add(content_container)

        # Footer
        self.footer = self.create_footer()
        self.main_box.add(self.footer)

    def create_header(self):
        """Create the header section"""
        header_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0),
            alignment='center',
            background_color=self.theme['header_background']
        ))

        # Left section - Logo and title
        left_section = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 20),
            alignment='center'
        ))

        logo_label = toga.Label(
            '📦',  # This could be replaced with an actual logo image
            style=Pack(
                font_size=24,
                padding=(0, 10, 0, 0)
            )
        )
        left_section.add(logo_label)

        title = toga.Label(
            'NexusWare',
            style=Pack(
                font_size=20,
                font_weight='bold',
                color=self.theme['header_text']
            )
        )
        left_section.add(title)

        header_box.add(left_section)

        # Center section - Navigation menu
        nav_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 0),
            flex=1,
            alignment='center'
        ))

        nav_items = [
            ('Inventory', 'inventory', '📋'),
            ('Tasks', 'tasks', '✓'),
            ('Pick Lists', 'pick_lists', '📝'),
            ('Scanner', 'barcode_scanner', '📱')
        ]

        for label, route, icon in nav_items:
            nav_item = toga.Box(style=Pack(
                direction=ROW,
                padding=(0, 10)
            ))

            btn = toga.Button(
                f'{icon} {label}',
                on_press=lambda w, r=route: self.navigate_to(r),
                style=Pack(
                    padding=(5, 10),
                    font_size=14,
                    color=self.theme['nav_text'],
                    background_color=self.theme['nav_background']
                )
            )
            nav_item.add(btn)
            nav_box.add(nav_item)

        header_box.add(nav_box)

        # Right section - User menu
        self.user_menu_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 20),
            alignment='center'
        ))

        # Will be populated in update_user_menu()
        header_box.add(self.user_menu_box)

        return header_box

    def create_footer(self):
        """Create the footer section"""
        footer_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 5),
            background_color=self.theme['footer_background']
        ))

        # Left section - Status
        status_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 10)
        ))

        self.connection_indicator = toga.Label(
            '🟢',  # Green circle for connected status
            style=Pack(
                font_size=12,
                padding=(0, 5, 0, 0)
            )
        )
        status_box.add(self.connection_indicator)

        self.status_label = toga.Label(
            'Connected',
            style=Pack(
                font_size=12,
                color=self.theme['footer_text']
            )
        )
        status_box.add(self.status_label)

        footer_box.add(status_box)

        # Center section - Message area
        self.message_label = toga.Label(
            '',
            style=Pack(
                font_size=12,
                color=self.theme['footer_text'],
                flex=1,
                text_align='center'
            )
        )
        footer_box.add(self.message_label)

        # Right section - Version and system info
        info_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 10)
        ))

        version_label = toga.Label(
            'v1.0.0',
            style=Pack(
                font_size=12,
                color=self.theme['footer_text'],
                padding=(0, 20, 0, 0)
            )
        )
        info_box.add(version_label)

        footer_box.add(info_box)

        return footer_box

    def update_user_menu(self):
        """Update user menu with current user data"""
        self.user_menu_box.clear()

        if self.user_data:
            user_label = toga.Label(
                self.user_data.username,
                style=Pack(
                    font_size=14,
                    color=self.theme['header_text'],
                    padding=(0, 10, 0, 0)
                )
            )
            self.user_menu_box.add(user_label)

            menu_btn = toga.Button(
                '⋮',
                on_press=self.show_user_menu,
                style=Pack(
                    padding=(5, 10),
                    font_size=16,
                    color=self.theme['header_text'],
                    background_color='transparent'
                )
            )
            self.user_menu_box.add(menu_btn)

    def show_user_menu(self, widget):
        """Show user menu dropdown"""
        menu = toga.Group('User Menu')

        commands = [
            ('👤 Profile', self.on_profile_press),
            ('⚙️ Settings', self.on_settings_press),
            ('🔒 Logout', self.on_logout_press)
        ]

        for label, handler in commands:
            cmd = toga.Command(
                lambda x: handler(),
                label,
                group=menu
            )
            self.window.app.commands.add(cmd)

    def show_loading(self, show: bool = True):
        """Show or hide loading overlay"""
        self.loading_overlay.style.update(
            display='flex' if show else 'none'
        )

    def show_error(self, message: str):
        """Display error message"""
        self.window.error_dialog('Error', message)
        self.message_label.text = f'Error: {message}'
        self.message_label.style.update(color=self.theme['error'])

    def show_success(self, message: str):
        """Display success message"""
        self.window.info_dialog('Success', message)
        self.message_label.text = message
        self.message_label.style.update(color=self.theme['success'])

    def show_warning(self, message: str):
        """Display warning message"""
        self.window.info_dialog('Warning', message)
        self.message_label.text = f'Warning: {message}'
        self.message_label.style.update(color=self.theme['warning'])

    def navigate_to(self, route: str, **params):
        """Navigate to another screen"""
        self.window.app.navigate_to(route, **params)

    async def on_logout_press(self):
        """Handle logout"""
        try:
            # Clear tokens and cache
            self.api_client.set_tokens("", "", 0)
            self.cache.clear()
            self.navigate_to('login')
        except Exception as e:
            self.show_error(str(e))

    def on_profile_press(self):
        """Navigate to profile screen"""
        self.navigate_to('profile')

    def on_settings_press(self):
        """Navigate to settings screen"""
        self.navigate_to('settings')

    def cleanup(self):
        """Cleanup before screen is destroyed"""
        pass

    async def refresh(self):
        """Refresh screen data"""
        pass

    def format_date(self, timestamp: int | None) -> str:
        """Format timestamp to date string"""
        if not timestamp:
            return '-'
        from datetime import datetime, timezone
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')

    def format_currency(self, amount: float) -> str:
        """Format amount as currency"""
        return f"${amount:,.2f}"

    def validate_required_fields(self, fields: dict) -> bool:
        """Validate required fields"""
        missing = [k for k, v in fields.items() if not v]
        if missing:
            self.show_error(f"Required fields missing: {', '.join(missing)}")
            return False
        return True
