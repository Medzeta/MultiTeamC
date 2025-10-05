"""
Flet Custom Dialogs
Custom dialogs to replace OS popups
"""

import flet as ft
from core.flet_theme import Theme
from core.debug_logger import debug, info


class CustomDialog:
    """Custom dialog system"""
    
    @staticmethod
    def show_error(page: ft.Page, title: str, message: str, on_close=None):
        """
        Show error dialog
        
        Args:
            page: Flet page
            title: Dialog title
            message: Error message
            on_close: Callback when closed
        """
        debug("CustomDialog", f"Showing error: {title}")
        
        def close_dialog(e):
            dialog.open = False
            page.update()
            if on_close:
                on_close()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon("error", color=Theme.ERROR, size=24),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=close_dialog,
                    style=ft.ButtonStyle(
                        color=Theme.ERROR,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
        
        info("CustomDialog", f"Error dialog shown: {title}")
    
    @staticmethod
    def show_success(page: ft.Page, title: str, message: str, on_close=None):
        """
        Show success dialog
        
        Args:
            page: Flet page
            title: Dialog title
            message: Success message
            on_close: Callback when closed
        """
        debug("CustomDialog", f"Showing success: {title}")
        
        def close_dialog(e):
            dialog.open = False
            page.update()
            if on_close:
                on_close()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon("check_circle", color=Theme.SUCCESS, size=24),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=close_dialog,
                    style=ft.ButtonStyle(
                        color=Theme.SUCCESS,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
        
        info("CustomDialog", f"Success dialog shown: {title}")
    
    @staticmethod
    def show_confirm(page: ft.Page, title: str, message: str, on_confirm=None, on_cancel=None):
        """
        Show confirmation dialog
        
        Args:
            page: Flet page
            title: Dialog title
            message: Confirmation message
            on_confirm: Callback when confirmed
            on_cancel: Callback when cancelled
        """
        debug("CustomDialog", f"Showing confirm: {title}")
        
        def confirm(e):
            dialog.open = False
            page.update()
            if on_confirm:
                on_confirm()
        
        def cancel(e):
            dialog.open = False
            page.update()
            if on_cancel:
                on_cancel()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon("help_outline", color=Theme.WARNING, size=24),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=cancel,
                    style=ft.ButtonStyle(
                        color=Theme.TEXT_SECONDARY,
                    ),
                ),
                ft.TextButton(
                    "Confirm",
                    on_click=confirm,
                    style=ft.ButtonStyle(
                        color=Theme.PRIMARY,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
        
        info("CustomDialog", f"Confirm dialog shown: {title}")
    
    @staticmethod
    def show_info(page: ft.Page, title: str, message: str, on_close=None):
        """
        Show info dialog
        
        Args:
            page: Flet page
            title: Dialog title
            message: Info message
            on_close: Callback when closed
        """
        debug("CustomDialog", f"Showing info: {title}")
        
        def close_dialog(e):
            dialog.open = False
            page.update()
            if on_close:
                on_close()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon("info_outline", color=Theme.PRIMARY, size=24),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=close_dialog,
                    style=ft.ButtonStyle(
                        color=Theme.PRIMARY,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
        
        info("CustomDialog", f"Info dialog shown: {title}")


# Export
__all__ = ['CustomDialog']
