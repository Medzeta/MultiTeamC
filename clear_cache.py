"""
Clear Python cache files
"""
import os
import shutil
from pathlib import Path

def clear_cache():
    """Remove all __pycache__ directories and .pyc files"""
    root_dir = Path(__file__).parent
    
    # Remove __pycache__ directories
    for pycache_dir in root_dir.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            print(f"✅ Removed: {pycache_dir}")
        except Exception as e:
            print(f"❌ Failed to remove {pycache_dir}: {e}")
    
    # Remove .pyc files
    for pyc_file in root_dir.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            print(f"✅ Removed: {pyc_file}")
        except Exception as e:
            print(f"❌ Failed to remove {pyc_file}: {e}")
    
    print("\n✅ Cache cleared successfully!")
    print("Now run: python main.py")

if __name__ == "__main__":
    clear_cache()
