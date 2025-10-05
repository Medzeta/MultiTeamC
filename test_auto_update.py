"""
Test script för auto-update systemet
Simulerar en tillgänglig uppdatering för att testa UI
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from core.auto_update_manager import UpdateDialog
from core.pyqt_theme import Theme

def test_update_dialog():
    """Testa update dialog"""
    app = QApplication(sys.argv)
    app.setStyleSheet(Theme.get_stylesheet())
    
    # Simulera uppdateringsdata
    fake_update_data = {
        'download_url': 'https://fake-url.com/update.zip',
        'asset_name': 'MultiTeam_v0.26.zip',
        'latest_version': '0.26',
        'current_version': '0.25'
    }
    
    # Skapa dialog
    dialog = UpdateDialog(
        parent=None,
        latest_version="0.26",
        current_version="0.25"
    )
    
    # Visa dialog
    dialog.show()
    
    # Kör app
    sys.exit(app.exec())

if __name__ == "__main__":
    test_update_dialog()
