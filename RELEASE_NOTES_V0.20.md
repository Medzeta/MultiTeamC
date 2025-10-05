# MultiTeam v0.20 - Auto-Update & Dynamic Assets Release

## 🚀 Major Features

### **Dynamic Asset System**
- **Auto-scanning Dashboard**: Automatically creates module cards from images in `assets/` folder
- **Real-time Updates**: 5-second auto-refresh detects new/removed assets instantly
- **Universal Format Support**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Seamless Integration**: Drop images in assets folder → cards appear automatically

### **Auto-Update System**
- **GitHub Integration**: Checks for updates from GitHub releases automatically
- **One-Click Updates**: Download and install updates directly from the app
- **Smart Versioning**: Compares versions and shows update availability
- **Backup & Restore**: Automatic backup before updates with rollback capability
- **Restart Management**: Automatic application restart after successful updates

### **Enhanced User Experience**
- **Clickable Module Cards**: Every asset becomes a functional module page
- **Coming Soon Pages**: Professional placeholder pages for all modules
- **Settings Integration**: Auto-updater accessible via Settings card
- **Version Display**: Current version shown in update interface

## 🔧 Technical Improvements

### **Version Management**
- **Centralized Versioning**: `core/version.py` manages all version info
- **Build Integration**: Version info embedded in build process
- **API Integration**: GitHub API for release checking and downloading

### **Release Automation**
- **GitHub Release Pipeline**: `release_github.bat` automates entire release process
- **Build → Zip → Publish**: Complete automation from source to GitHub release
- **Multiple Auth Methods**: GitHub CLI or Personal Access Token support
- **Asset Management**: Automatic ZIP creation and upload

### **Module System Enhancement**
- **Dynamic Page Generation**: Automatic undersida creation for each asset
- **Signal-based Navigation**: Clean back/forward navigation
- **Modular Architecture**: Easy to extend with new modules

## 📁 New Files Added

### Core System
- `core/version.py` - Version management and auto-update logic
- `modules_pyqt/auto_update_module.py` - Auto-update UI module
- `modules_pyqt/dynamic_module_page.py` - Dynamic page generator

### Release Automation
- `release_github.bat` - Main release automation script
- `scripts/upload_release.ps1` - GitHub API upload fallback
- `UPDATE_RELEASE_GUIDE.md` - Complete setup and usage guide
- `RELEASE_NOTES_V0.20.md` - This release notes file

## 🎯 User Benefits

### **For End Users**
- **Automatic Updates**: Never miss important updates - get notified automatically
- **Easy Installation**: One-click update download and installation
- **Modular Experience**: Add new functionality by simply adding images
- **Professional Interface**: Consistent, polished UI throughout

### **For Developers**
- **Release Automation**: Push updates to users with single command
- **Version Control**: Centralized version management
- **Easy Extension**: Add new modules by dropping images in assets folder
- **GitHub Integration**: Leverages GitHub releases for distribution

## 🔄 How Auto-Update Works

1. **Check**: App periodically checks GitHub for new releases
2. **Notify**: User sees update notification in Settings
3. **Download**: One-click download of update package
4. **Install**: Automatic installation with backup creation
5. **Restart**: Seamless restart to new version

## 📦 How Dynamic Assets Work

1. **Drop Image**: Place any supported image in `assets/` folder
2. **Auto-Detect**: Dashboard scans and creates card within 5 seconds
3. **Click & Navigate**: Card becomes clickable with automatic page generation
4. **Remove**: Delete image → card disappears automatically

## 🚀 Release Process

### For Developers
```bash
# Simple release command
release_github.bat 0.20

# Or with custom version
release_github.bat 1.0.0
```

### For Users
1. Open app → Click Settings card
2. Click "Check for Updates"
3. If update available → Click "Download Update"
4. Click "Install & Restart"
5. Enjoy new version!

## 🔧 System Requirements

- **Windows 10/11**
- **Internet connection** (for updates and email verification)
- **GitHub CLI** (recommended) or **Personal Access Token** (for developers)

## 🎉 What's Next

- **Client-Side Auto-Check**: Automatic background update checking
- **Module Store**: Download additional modules from repository
- **Plugin System**: Third-party module support
- **Advanced Settings**: Update frequency and notification preferences

---

**Full Changelog**: https://github.com/Medzeta/Multi-Team-C/releases/tag/v0.20

**Download**: [MultiTeam_Package_v0.20.zip](https://github.com/Medzeta/Multi-Team-C/releases/download/v0.20/MultiTeam_Package_v0.20.zip)

© 2025 MultiTeam Communication. All rights reserved.
