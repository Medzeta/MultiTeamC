"""
Test app för Modern Login Module
Visar den nya designen enligt uppdaterad GLOBAL_DESIGN.md
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from core.pyqt_theme import Theme
from modules_pyqt.modern_login_module import ModernLoginModule
from core.debug_logger import debug, info


class TestWindow(QMainWindow):
    """Test window för modern login module"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Multi Team -C - Modern Login Test")
        self.setGeometry(100, 100, 1400, 900)
        
        # Sätt bakgrundsfärg enligt tema
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Theme.BACKGROUND};
            }}
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Skapa modern login module
        self.login_module = ModernLoginModule()
        
        # Koppla signals
        self.login_module.login_success.connect(self._on_login_success)
        self.login_module.register_clicked.connect(self._on_register_clicked)
        self.login_module.forgot_password_clicked.connect(self._on_forgot_password)
        self.login_module.license_clicked.connect(self._on_license_clicked)
        
        layout.addWidget(self.login_module)
        
        # Applicera global stylesheet
        self.setStyleSheet(Theme.get_stylesheet())
        
        info("TestWindow", "Test window created with modern login module")
    
    def _on_login_success(self, user_data):
        """Hantera lyckad inloggning"""
        info("TestWindow", f"Login success: {user_data}")
        print(f"✅ Login successful: {user_data['email']}")
    
    def _on_register_clicked(self):
        """Hantera registrering"""
        info("TestWindow", "Register clicked")
        print("📝 Register button clicked")
    
    def _on_forgot_password(self):
        """Hantera glömt lösenord"""
        info("TestWindow", "Forgot password clicked")
        print("🔑 Forgot password clicked")
    
    def _on_license_clicked(self):
        """Hantera licensaktivering"""
        info("TestWindow", "License activation clicked")
        print("🔐 License activation clicked")


def main():
    """Huvudfunktion"""
    app = QApplication(sys.argv)
    
    # Sätt mörkt tema
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(58, 58, 58))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(58, 58, 58))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(31, 106, 165))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(31, 106, 165))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Skapa och visa test window
    window = TestWindow()
    window.show()
    
    print("🚀 Modern Login Test App Started")
    print("📋 Features to test:")
    print("   • Rektangulär login-ruta (420x580px)")
    print("   • Rundade hörn (12px)")
    print("   • Subtila färgövergångar")
    print("   • Kompakt textfält design")
    print("   • Hover-effekter på knappar och textfält")
    print("   • Focus-border på textfält")
    print("   • Modern checkbox design")
    print("   • SuperAdmin login: email=1, password=1")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
