"""
Build Script - Skapar EXE från Python applikationen
Använder PyInstaller för att skapa standalone executable
"""

import os
import sys
import shutil
from pathlib import Path
from core.debug_logger import debug, info, warning, error

def clean_build_dirs():
    """Rensa gamla build directories"""
    info("BUILD", "Cleaning old build directories...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            debug("BUILD", f"Removing directory: {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)
            info("BUILD", f"Removed: {dir_path}")
    
    # Clean .spec files
    for spec_file in Path(".").glob("*.spec"):
        debug("BUILD", f"Removing spec file: {spec_file}")
        spec_file.unlink()
        info("BUILD", f"Removed: {spec_file}")
    
    info("BUILD", "Cleanup completed")

def check_dependencies():
    """Kontrollera att alla dependencies är installerade"""
    info("BUILD", "Checking dependencies...")
    
    # Package name mapping: import_name -> pip_name
    required_packages = {
        "PyQt6": "PyQt6",
        "PIL": "pillow", 
        "cryptography": "cryptography",
        "zmq": "pyzmq",
        "pydantic": "pydantic", 
        "bcrypt": "bcrypt",
        "PyInstaller": "pyinstaller",
        "requests": "requests"
    }
    
    missing_packages = []
    
    for import_name, pip_name in required_packages.items():
        try:
            __import__(import_name)
            debug("BUILD", f"✓ {import_name} installed")
        except ImportError:
            warning("BUILD", f"✗ {import_name} NOT installed")
            missing_packages.append(pip_name)
    
    if missing_packages:
        error("BUILD", f"Missing packages: {', '.join(missing_packages)}")
        print("\n❌ Missing required packages!")
        print(f"   Install with: pip install {' '.join(missing_packages)}")
        return False
    
    info("BUILD", "All dependencies installed ✓")
    return True

def build_exe():
    """Bygg EXE med PyInstaller"""
    info("BUILD", "Starting EXE build process...")
    
    # PyInstaller command - use python -m PyInstaller for Windows Store Python
    cmd = [
        "python", "-m", "PyInstaller",
        "--name=MultiTeam",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        # Add data files - use correct PyQt6 paths
        "--add-data=core;core",
        "--add-data=modules_pyqt;modules_pyqt",
        "--add-data=assets;assets",
        # Hidden imports for PyQt6
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets", 
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=bcrypt",
        "--hidden-import=cryptography",
        "--hidden-import=requests",
        # Exclude unnecessary modules
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=tkinter",
        # Main file - use PyQt6 version
        "main_pyqt.py"
    ]
    
    debug("BUILD", f"PyInstaller command: {' '.join(cmd)}")
    
    # Run PyInstaller
    import subprocess
    
    try:
        info("BUILD", "Running PyInstaller...")
        debug("BUILD", f"Working directory: {os.getcwd()}")
        debug("BUILD", f"Command: {' '.join(cmd)}")
        
        # Run with real-time output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 text=True, universal_newlines=True)
        
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                output_lines.append(line)
                debug("BUILD", f"PyInstaller: {line}")
        
        rc = process.poll()
        
        if rc == 0:
            info("BUILD", "EXE build completed successfully! ✓")
            
            # Check if EXE was actually created
            exe_path = Path("dist") / "MultiTeam.exe"
            if exe_path.exists():
                info("BUILD", f"✓ EXE created: {exe_path} ({exe_path.stat().st_size} bytes)")
            else:
                error("BUILD", "❌ EXE file not found despite successful PyInstaller run")
                return False
            
            return True
        else:
            error("BUILD", f"PyInstaller failed with exit code: {rc}")
            error("BUILD", "Last 10 lines of output:")
            for line in output_lines[-10:]:
                error("BUILD", f"  {line}")
            return False
        
    except FileNotFoundError as e:
        error("BUILD", f"PyInstaller not found: {e}")
        error("BUILD", "Try: pip install pyinstaller")
        return False
    except Exception as e:
        error("BUILD", f"Unexpected error during build: {e}")
        return False

def create_dist_package():
    """Skapa distribution package med EXE och nödvändiga filer"""
    info("BUILD", "Creating distribution package...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        error("BUILD", "dist directory not found!")
        return False
    
    # Create package directory
    package_dir = dist_dir / "MultiTeam_Package"
    package_dir.mkdir(exist_ok=True)
    debug("BUILD", f"Package directory: {package_dir}")
    
    # Copy EXE
    exe_file = dist_dir / "MultiTeam.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, package_dir / "MultiTeam.exe")
        info("BUILD", "✓ Copied MultiTeam.exe")
    else:
        error("BUILD", "MultiTeam.exe not found!")
        return False
    
    # Copy README
    readme_file = Path("README.md")
    if readme_file.exists():
        shutil.copy2(readme_file, package_dir / "README.md")
        info("BUILD", "✓ Copied README.md")
    
    # Copy ROADMAP
    roadmap_file = Path("ROADMAP.md")
    if roadmap_file.exists():
        shutil.copy2(roadmap_file, package_dir / "ROADMAP.md")
        info("BUILD", "✓ Copied ROADMAP.md")
    
    # Create data and logs directories
    (package_dir / "data").mkdir(exist_ok=True)
    (package_dir / "logs").mkdir(exist_ok=True)
    info("BUILD", "✓ Created data and logs directories")
    
    # Create quick start guide
    quick_start = package_dir / "QUICK_START.txt"
    with open(quick_start, "w", encoding="utf-8") as f:
        f.write("""
╔══════════════════════════════════════════════════════════════╗
║         MultiTeam P2P Communication - Quick Start            ║
╚══════════════════════════════════════════════════════════════╝

1. STARTA APPLIKATIONEN
   - Dubbelklicka på MultiTeam.exe

2. SUPERADMIN LOGIN
   Email:    admin@multiteam.local
   Password: SuperAdmin123!

3. SKAPA NYTT KONTO
   - Klicka på "Create New Account"
   - Fyll i dina uppgifter
   - Verifiera din email med koden som skickas

4. SUPPORT
   - Läs README.md för mer information
   - Kontrollera ROADMAP.md för planerade features
   - Loggar sparas i logs/ mappen

5. SYSTEMKRAV
   - Windows 10 eller 11
   - Internetanslutning (för email-verifiering)

╔══════════════════════════════════════════════════════════════╗
║  Version 0.1.0 (Alpha) - © 2025 MultiTeam Communication     ║
╚══════════════════════════════════════════════════════════════╝
""")
    info("BUILD", "✓ Created QUICK_START.txt")
    
    info("BUILD", f"Distribution package created: {package_dir}")
    return True

def main():
    """Main build process"""
    from core.version import APP_VERSION, VERSION_INFO
    
    print("\n" + "="*60)
    print(f"  MultiTeam P2P Communication - EXE Builder v{APP_VERSION}")
    print("="*60)
    print(f"  Build Date: {VERSION_INFO['build_date']}")
    print(f"  Build Type: {VERSION_INFO['build_type']}")
    print("="*60 + "\n")
    
    # Step 1: Clean
    print("Step 1: Cleaning old builds...")
    clean_build_dirs()
    print("✓ Cleanup completed\n")
    
    # Step 2: Check dependencies
    print("Step 2: Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Build failed: Missing dependencies")
        return 1
    print("✓ All dependencies OK\n")
    
    # Step 3: Build EXE
    print("Step 3: Building EXE with PyInstaller...")
    print("   (This may take a few minutes...)\n")
    if not build_exe():
        print("\n❌ Build failed: PyInstaller error")
        return 1
    print("✓ EXE build completed\n")
    
    # Step 4: Create package
    print("Step 4: Creating distribution package...")
    if not create_dist_package():
        print("\n❌ Build failed: Package creation error")
        return 1
    print("✓ Package created\n")
    
    # Success
    print("="*60)
    print("  ✓ BUILD SUCCESSFUL!")
    print("="*60)
    print("\nYour executable is ready:")
    print("  📦 dist/MultiTeam_Package/MultiTeam.exe")
    print("\nDistribution package includes:")
    print("  • MultiTeam.exe")
    print("  • README.md")
    print("  • ROADMAP.md")
    print("  • QUICK_START.txt")
    print("  • data/ (for database)")
    print("  • logs/ (for debug logs)")
    print("\nYou can now distribute the entire MultiTeam_Package folder.")
    print("\n" + "="*60 + "\n")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
