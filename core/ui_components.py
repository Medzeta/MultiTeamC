"""
Global UI Components System
Alla custom buttons, inputs, och UI element definieras här
"""

import customtkinter as ctk
from typing import Optional, Callable
from core.debug_logger import debug, info


class CustomButton(ctk.CTkButton):
    """Custom styled button"""
    
    def __init__(
        self,
        master,
        text: str = "Button",
        command: Optional[Callable] = None,
        width: int = 200,
        height: int = 40,
        style: str = "primary",
        **kwargs
    ):
        """Initialize custom button"""
        debug("CustomButton", f"Creating button: {text} (style: {style})")
        
        # Style presets
        styles = {
            "primary": {
                "fg_color": ("#1f6aa5", "#144870"),
                "hover_color": ("#1a5a8f", "#0f3a5f"),
                "text_color": "#ffffff"
            },
            "secondary": {
                "fg_color": ("#3a3a3a", "#2a2a2a"),
                "hover_color": ("#4a4a4a", "#3a3a3a"),
                "text_color": "#ffffff"
            },
            "success": {
                "fg_color": ("#107c10", "#0d5e0d"),
                "hover_color": ("#0e6b0e", "#0a4d0a"),
                "text_color": "#ffffff"
            },
            "danger": {
                "fg_color": ("#c42b1c", "#a02318"),
                "hover_color": ("#a02318", "#8a1f15"),
                "text_color": "#ffffff"
            },
            "transparent": {
                "fg_color": "transparent",
                "hover_color": ("#2a2a2a", "#1a1a1a"),
                "text_color": "#ffffff"
            }
        }
        
        style_config = styles.get(style, styles["primary"])
        
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            font=("Segoe UI", 12),
            corner_radius=6,
            **{**style_config, **kwargs}
        )
        
        debug("CustomButton", f"Button created: {text}")


class CustomEntry(ctk.CTkEntry):
    """Custom styled entry field"""
    
    def __init__(
        self,
        master,
        placeholder: str = "",
        width: int = 300,
        height: int = 40,
        show: str = "",
        **kwargs
    ):
        """Initialize custom entry"""
        debug("CustomEntry", f"Creating entry field: {placeholder}")
        super().__init__(
            master,
            placeholder_text=placeholder,
            width=width,
            height=height,
            font=("Segoe UI", 12),
            text_color=("#ffffff", "#ffffff"),  # Vit text
            corner_radius=6,
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            fg_color=("#2b2b2b", "#2b2b2b"),  # Samma som app bakgrund
            **kwargs
        )
        
        debug("CustomEntry", f"Entry field created: {placeholder}")
    
    def get_value(self) -> str:
        """Get entry value with debug logging"""
        value = self.get()
        debug("CustomEntry", f"Getting value: {len(value)} characters")
        return value
    
    def set_value(self, value: str):
        """Set entry value with debug logging"""
        debug("CustomEntry", f"Setting value: {len(value)} characters")
        self.delete(0, "end")
        self.insert(0, value)


class CustomLabel(ctk.CTkLabel):
    """Custom styled label"""
    
    def __init__(
        self,
        master,
        text: str = "",
        size: int = 12,
        bold: bool = False,
        color: Optional[str] = None,
        **kwargs
    ):
        """Initialize custom label"""
        debug("CustomLabel", f"Creating label: {text[:30]}...")
        
        font_weight = "bold" if bold else "normal"
        text_color = color if color else ("#ffffff", "#ffffff")
        
        super().__init__(
            master,
            text=text,
            font=("Segoe UI", size, font_weight),
            text_color=text_color,
            **kwargs
        )
        
        debug("CustomLabel", f"Label created")


class CustomFrame(ctk.CTkFrame):
    """Custom styled frame"""
    
    def __init__(
        self,
        master,
        transparent: bool = False,
        **kwargs
    ):
        """Initialize custom frame"""
        debug("CustomFrame", f"Creating frame (transparent: {transparent})")
        
        fg_color = "transparent" if transparent else ("#2b2b2b", "#2b2b2b")  # Ljus grå
        
        super().__init__(
            master,
            fg_color=fg_color,
            corner_radius=8,
            **kwargs
        )
        
        debug("CustomFrame", "Frame created")


class CustomCheckbox(ctk.CTkCheckBox):
    """Custom styled checkbox"""
    
    def __init__(
        self,
        master,
        text: str = "",
        command: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize custom checkbox"""
        debug("CustomCheckbox", f"Creating checkbox: {text}")
        
        super().__init__(
            master,
            text=text,
            command=command,
            font=("Segoe UI", 10),
            text_color=("#ffffff", "#ffffff"),  # Vit text
            checkbox_width=16,
            checkbox_height=16,
            corner_radius=3,
            border_width=2,
            fg_color=("#1f6aa5", "#144870"),
            hover_color=("#1a5a8f", "#0f3a5f"),
            **kwargs
        )
        
        debug("CustomCheckbox", f"Checkbox created: {text}")


class LoadingSpinner(ctk.CTkLabel):
    """Custom loading spinner"""
    
    def __init__(self, master, size: int = 40):
        """Initialize loading spinner"""
        debug("LoadingSpinner", f"Creating spinner (size: {size})")
        
        super().__init__(
            master,
            text="⟳",
            font=("Segoe UI", size),
            text_color=("#1f6aa5", "#144870")
        )
        
        self._spinning = False
        self._rotation = 0
        debug("LoadingSpinner", "Spinner created")
    
    def start(self):
        """Start spinner animation"""
        debug("LoadingSpinner", "Starting spinner")
        self._spinning = True
        self._animate()
    
    def stop(self):
        """Stop spinner animation"""
        debug("LoadingSpinner", "Stopping spinner")
        self._spinning = False
    
    def _animate(self):
        """Animate spinner rotation"""
        if self._spinning:
            self._rotation = (self._rotation + 30) % 360
            self.after(50, self._animate)


class MessageBox:
    """Custom message box / alert dialog"""
    
    @staticmethod
    def show_info(parent, title: str, message: str):
        """Show info message"""
        debug("MessageBox", f"Showing info: {title}")
        from core.custom_window import CustomDialog
        
        dialog = CustomDialog(parent, title=title, width=320, height=180)
        
        content = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=15, pady=15)
        
        # Message (white text, no card - same color throughout)
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Segoe UI", 11),
            text_color=("#ffffff", "#ffffff"),
            wraplength=280,
            justify="center"
        )
        msg_label.pack(expand=True, pady=(5, 15))
        
        # OK button with border (visible)
        ok_btn = CustomButton(
            content,
            text="OK",
            command=dialog._close_dialog,
            width=120,
            height=36,
            border_width=1,
            border_color=("#1f6aa5", "#144870")
        )
        ok_btn.pack(pady=(0, 5))
        
        info("MessageBox", f"Info dialog shown: {title}")
        return dialog
    
    @staticmethod
    def show_error(parent, title: str, message: str):
        """Show error message"""
        debug("MessageBox", f"Showing error: {title}")
        from core.custom_window import CustomDialog
        
        dialog = CustomDialog(parent, title=title, width=280, height=150)
        
        content = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=12, pady=8)
        
        # Message (white text, no icon)
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Segoe UI", 12),
            text_color=("#ffffff", "#ffffff"),
            wraplength=300,
            justify="center"
        )
        msg_label.pack(expand=True, pady=(10, 15))
        
        # OK button with border
        ok_btn = CustomButton(
            content,
            text="OK",
            command=dialog._close_dialog,
            width=120,
            height=36,
            style="danger",
            border_width=1,
            border_color=("#c42b1c", "#a02318")
        )
        ok_btn.pack(pady=(0, 10))
        
        info("MessageBox", f"Error dialog shown: {title}")
        return dialog
    
    @staticmethod
    def show_success(parent, title: str, message: str):
        """Show success message"""
        debug("MessageBox", f"Showing success: {title}")
        from core.custom_window import CustomDialog
        
        dialog = CustomDialog(parent, title=title, width=400, height=220)
        
        content = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Message (white text, no icon)
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Segoe UI", 12),
            text_color=("#ffffff", "#ffffff"),
            wraplength=350,
            justify="center"
        )
        msg_label.pack(expand=True, pady=(10, 20))
        
        # OK button with border
        ok_btn = CustomButton(
            content,
            text="OK",
            command=dialog._close_dialog,
            width=120,
            height=36,
            style="success",
            border_width=1,
            border_color=("#107c10", "#0d5e0d")
        )
        ok_btn.pack(pady=(0, 10))
        
        info("MessageBox", f"Success dialog shown: {title}")
        return dialog
    
    @staticmethod
    def show_confirm(parent, title: str, message: str, on_confirm: Callable):
        """Show confirmation dialog"""
        debug("MessageBox", f"Showing confirm: {title}")
        from core.custom_window import CustomDialog
        
        dialog = CustomDialog(parent, title=title, width=300, height=160)
        
        content = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=12, pady=8)
        
        # Message (white text, no icon)
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Segoe UI", 12),
            text_color=("#ffffff", "#ffffff"),
            wraplength=300,
            justify="center"
        )
        msg_label.pack(expand=True, pady=(10, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(pady=(15, 5))
        
        def on_yes():
            debug("MessageBox", "Confirm dialog: OK clicked")
            dialog._close_dialog()
            on_confirm()
        
        def on_no():
            debug("MessageBox", "Confirm dialog: Cancel clicked")
            dialog._close_dialog()
        
        # OK button with border
        yes_btn = CustomButton(
            btn_frame,
            text="OK",
            command=on_yes,
            width=110,
            height=40,
            style="success",
            border_width=1,
            border_color=("#107c10", "#0d5e0d")
        )
        yes_btn.pack(side="left", padx=5)
        
        # Cancel button with border
        no_btn = CustomButton(
            btn_frame,
            text="Cancel",
            command=on_no,
            width=110,
            height=40,
            style="secondary",
            border_width=1,
            border_color=("#4a4a4a", "#4a4a4a")
        )
        no_btn.pack(side="left", padx=5)
        
        info("MessageBox", f"Confirm dialog shown: {title}")
        return dialog


if __name__ == "__main__":
    # Test UI components
    info("TEST", "Testing UI Components...")
    
    app = ctk.CTk()
    app.geometry("600x500")
    ctk.set_appearance_mode("dark")
    
    frame = CustomFrame(app)
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    CustomLabel(frame, text="UI Components Test", size=20, bold=True).pack(pady=10)
    
    CustomButton(frame, text="Primary Button", style="primary").pack(pady=5)
    CustomButton(frame, text="Secondary Button", style="secondary").pack(pady=5)
    CustomButton(frame, text="Success Button", style="success").pack(pady=5)
    CustomButton(frame, text="Danger Button", style="danger").pack(pady=5)
    
    CustomEntry(frame, placeholder="Enter text here").pack(pady=10)
    
    CustomCheckbox(frame, text="Remember me").pack(pady=5)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()
