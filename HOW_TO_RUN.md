# How to Run MultiTeam P2P Communication

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- Windows OS (designed for Windows)

### Installation

1. **Install Dependencies**
```bash
pip install customtkinter
pip install cryptography
pip install pyotp
pip install qrcode
pip install pillow
pip install pystray
```

Or use requirements.txt (if created):
```bash
pip install -r requirements.txt
```

2. **Run the Application**
```bash
python main.py
```

## 👤 First Time Setup

### Option 1: Login as SuperAdmin
1. Launch the app
2. Click "Login"
3. Enter credentials:
   - **Development**: Username: `Dev`, Password: `Dev`
   - **Production**: Username: `SuperAdmin`, Password: `SuperSecure2024!`
4. Click "Login"

**Note**: SuperAdmin cannot use 2FA due to user_id=0 constraint.

### Option 2: Create New User
1. Launch the app
2. Click "Register"
3. Fill in:
   - Name
   - Email
   - Password (min 8 characters)
4. Click "Register"
5. Login with your new credentials
6. (Optional) Setup 2FA for extra security

## 🔐 Setting Up 2FA

1. Login to your account
2. Click "🔐 Setup 2FA" in dashboard
3. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
4. Enter 6-digit code to verify
5. Save backup codes in a safe place
6. Click "Complete Setup"

From now on, you'll need the 6-digit code when logging in.

## 👥 Creating Your First Team

1. Login to the app
2. Click "👥 Teams" button in dashboard
3. Click "+ Create Team"
4. Enter:
   - Team name
   - Description (optional)
5. Click "Create"

Your team is now created and you're the owner!

## 🌐 Connecting to Peers

### Automatic Discovery
The app automatically discovers other clients on your network using 6 different methods:

1. **UDP Broadcast** (3 ports)
2. **Multicast**
3. **TCP Servers** (6 ports)
4. **UDP Hole Punching**
5. **Multi-method Broadcast**
6. **Local Network Scan**

### Manual Connection
1. Click "🌐 Network Peers" in dashboard
2. Wait for peers to appear (usually 5-10 seconds)
3. Click "Connect" on a peer
4. Status will change to "Connected" (green)

**Tip**: The app tries multiple methods simultaneously, so it works through most firewalls and NAT configurations!

## 📨 Inviting Members to Team

1. Make sure peer is connected (green status in Network Peers)
2. Go to "👥 Teams"
3. Click on your team
4. Click "+ Invite" button
5. Select the peer from list
6. Click "Send Invitation"

The peer will receive the invitation via P2P and can accept it.

## 💬 Using Team Chat

1. Go to "👥 Teams"
2. Click on a team
3. Click "💬 Open Chat"
4. Type your message and press Enter
5. Messages sync automatically to all team members!

### Sending Files
1. In team chat, click the 📎 button
2. Select a file
3. File is sent to all connected team members
4. File is verified with SHA256 hash

## 🔧 Settings

Access settings from the dashboard:
- **Minimize to Tray**: App minimizes to system tray instead of taskbar
- **2FA Required**: Enforce 2FA for all users
- **Theme**: Dark theme (default)

## 📊 Understanding Status Indicators

### User Status (Top Right)
- 🟢 **Online** - Connected and ready
- 🟡 **Connecting** - Starting P2P system
- 🔴 **Offline** - Not connected

### Peer Status (Network Peers)
- 🟢 **Connected** - Active P2P connection
- 🟡 **Discovered** - Found but not connected
- 🔴 **Disconnected** - Connection lost

### Team Roles
- 🏷️ **Owner** - Full control, can't leave team
- 🏷️ **Admin** - Can invite members
- 🏷️ **Member** - Standard access

## 🐛 Troubleshooting

### Peers Not Showing Up
1. Check firewall settings (allow Python)
2. Make sure both clients are on same network
3. Wait 10-15 seconds for all discovery methods
4. Try clicking "Refresh" in Network Peers

### Can't Connect to Peer
1. Check if peer is online
2. Verify firewall isn't blocking ports
3. Try restarting both apps
4. Check if antivirus is blocking connections

### 2FA Not Working
1. Make sure time is synced on both devices
2. Check if authenticator app time is correct
3. Try using a backup code instead
4. If locked out, use backup codes

### File Transfer Fails
1. Check if peer is still connected
2. Verify file size (large files take longer)
3. Check disk space on receiving end
4. Try sending a smaller file first

### Chat Messages Not Syncing
1. Check if team members are connected
2. Verify P2P connection is active (green)
3. Wait a few seconds (auto-refresh every 3s)
4. Try clicking "Refresh" in chat

## 🔒 Security Best Practices

1. **Use 2FA**: Always enable 2FA for your account
2. **Strong Passwords**: Use at least 12 characters
3. **Backup Codes**: Save them in a secure location
4. **Regular Updates**: Keep the app updated
5. **Trusted Networks**: Only connect on trusted networks
6. **Verify Peers**: Make sure you know who you're connecting to

## 📁 Data Storage

All data is stored locally:
- **User Database**: `data/app.db`
- **Teams Database**: `data/teams.db`
- **P2P Config**: `data/p2p_config.json`
- **Encryption Keys**: `data/keys_*.json`
- **Received Files**: `data/files/`

**Backup Tip**: Regularly backup the `data/` folder to prevent data loss.

## 🌟 Advanced Features

### Multiple Teams
- You can be member of unlimited teams
- Each team has separate chat and files
- Data syncs independently per team

### Role Management
- **Owner**: Created the team, full control
- **Admin**: Can invite new members
- **Member**: Can chat and share files

### Offline Capability
- Messages are stored locally
- Sync happens when peers come online
- No central server required

### Encryption
- All messages encrypted with AES-256
- File transfers verified with SHA256
- Each peer has unique encryption keys

## 🎯 Use Cases

### Small Team Collaboration
Perfect for 2-10 people working together:
- Share files without cloud storage
- Chat without external servers
- Full privacy and control

### Distributed Teams
Works across different locations:
- P2P finds peers automatically
- Works through most firewalls
- No infrastructure needed

### Secure Communication
For privacy-conscious users:
- End-to-end encryption
- No data stored on servers
- You control your data

## 📞 Support

### Common Questions

**Q: Do I need a server?**
A: No! The app is fully P2P, no server needed.

**Q: Can peers on different networks connect?**
A: Currently designed for same network. For different networks, you'd need port forwarding or VPN.

**Q: How many peers can I connect to?**
A: No hard limit, but performance depends on your network.

**Q: Is my data encrypted?**
A: Yes! All communication uses AES-256 encryption.

**Q: Can I use this on Mac/Linux?**
A: The code is Python-based, but UI is optimized for Windows. May work on other OS with modifications.

## 🚀 Next Steps

1. **Create your first team**
2. **Invite some peers**
3. **Start chatting**
4. **Share some files**
5. **Enjoy secure P2P communication!**

---

**Need Help?** Check `FINAL_PROJECT_SUMMARY.md` for technical details or `ROADMAP.md` for development history.

**Happy Collaborating!** 🎉
