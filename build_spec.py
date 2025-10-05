"""
PyInstaller Build Specification
Skapar standalone EXE för MultiTeam P2P Communication
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_exe():
    """Build standalone EXE with PyInstaller"""
    
    print("=" * 60)
    print("Building MultiTeam P2P Communication EXE")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # PyInstaller arguments
    args = [
        'main.py',  # Main script
        '--name=MultiTeam',  # EXE name
        '--onefile',  # Single EXE file
        '--windowed',  # No console window
        '--icon=assets/icon.ico' if (project_root / 'assets' / 'icon.ico').exists() else '',
        
        # Add data files
        '--add-data=data;data',
        '--add-data=logs;logs',
        
        # Hidden imports
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=bcrypt',
        '--hidden-import=pyotp',
        '--hidden-import=qrcode',
        '--hidden-import=cryptography',
        '--hidden-import=cryptography.fernet',
        '--hidden-import=cryptography.hazmat.primitives',
        '--hidden-import=cryptography.hazmat.primitives.asymmetric',
        '--hidden-import=cryptography.hazmat.primitives.ciphers',
        '--hidden-import=cryptography.hazmat.backends',
        
        # Exclude unnecessary modules
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=pytest',
        
        # Clean build
        '--clean',
        
        # Output directory
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        
        # Debug options (comment out for production)
        # '--debug=all',
        # '--console',  # Show console for debugging
    ]
    
    # Remove empty strings
    args = [arg for arg in args if arg]
    
    print("\nPyInstaller arguments:")
    for arg in args:
        print(f"  {arg}")
    
    print("\nBuilding...")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("✅ Build completed successfully!")
        print(f"EXE location: {project_root / 'dist' / 'MultiTeam.exe'}")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Build failed: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    build_exe()
