# /clients/mobile/utils/api_helper.py

from typing import Callable

import flet as ft
import httpx


async def api_call(app, method: Callable, *args, **kwargs):
    try:
        async with httpx.AsyncClient() as client:
            response = await method(*args, **kwargs)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        error_message = f"HTTP error: {e.response.status_code} - {e.response.text}"
        show_error_snackbar(app, error_message)
        return None
    except httpx.RequestError as e:
        error_message = f"Request error: {str(e)}"
        show_error_snackbar(app, error_message)
        return None
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        show_error_snackbar(app, error_message)
        return None


def show_error_snackbar(app, message: str):
    app.page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        action="Dismiss"
    )
    app.page.snack_bar.open = True
    app.page.update()
