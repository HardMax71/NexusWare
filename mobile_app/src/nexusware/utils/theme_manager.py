# src/nexusware/utils/theme_manager.py
from typing import Dict


class ThemeManager:
    def __init__(self):
        self.current_theme = 'light'
        self.themes = {
            'light': self._get_light_theme(),
            'dark': self._get_dark_theme()
        }

    def _get_light_theme(self) -> Dict[str, str]:
        return {
            'background': '#f5f5f5',
            'content_background': '#ffffff',
            'header_background': '#3a9be5',
            'header_text': '#ffffff',
            'footer_background': '#f0f0f0',
            'footer_text': '#666666',
            'nav_background': 'transparent',
            'nav_text': '#ffffff',
            'button_background': '#3a9be5',
            'button_text': '#ffffff',
            'input_background': '#ffffff',
            'input_text': '#333333',
            'input_border': '#d0d0d0',
            'table_header': '#f0f0f0',
            'table_row': '#ffffff',
            'table_row_alt': '#f9f9f9',
            'error': '#dc3545',
            'success': '#28a745',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }

    def _get_dark_theme(self) -> Dict[str, str]:
        return {
            'background': '#1e1e1e',
            'content_background': '#2d2d2d',
            'header_background': '#000000',
            'header_text': '#ffffff',
            'footer_background': '#1e1e1e',
            'footer_text': '#999999',
            'nav_background': 'transparent',
            'nav_text': '#ffffff',
            'button_background': '#3a9be5',
            'button_text': '#ffffff',
            'input_background': '#3d3d3d',
            'input_text': '#ffffff',
            'input_border': '#505050',
            'table_header': '#2d2d2d',
            'table_row': '#3d3d3d',
            'table_row_alt': '#353535',
            'error': '#dc3545',
            'success': '#28a745',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }

    def get_theme(self, name: str | None = None) -> Dict[str, str]:
        """Get theme colors by name"""
        theme_name = name or self.current_theme
        return self.themes[theme_name]

    def switch_theme(self, name: str):
        """Switch current theme"""
        if name not in self.themes:
            raise ValueError(f"Theme {name} not found")
        self.current_theme = name

    def add_theme(self, name: str, theme: Dict[str, str]):
        """Add custom theme"""
        self.themes[name] = theme

    def get_style(self, element: str, theme: str | None = None) -> str:
        """Get style for specific element"""
        theme_colors = self.get_theme(theme)
        return theme_colors.get(element, theme_colors['background'])
