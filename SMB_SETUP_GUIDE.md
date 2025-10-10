# 📁 SMB File Server Integration - Setup Guide

## Overview

This guide will help you set up the SMB/CIFS file server integration for the PKP Material Delivery Dashboard. This feature allows your team to store, browse, upload, and download project files directly from the dashboard while they're physically stored on your office SMB file server.

---

## 🎯 What This Feature Does

### ✅ File Management
- **Browse** folders and files on your office SMB server
- **Upload** files directly from the dashboard to the server
- **Download** files from the server to your computer
- **Delete** files with confirmation
- **Create** new folders with proper organization
- **Search** and filter files across projects

### ✅ Organization
- Automatic folder structure by project
- Breadcrumb navigation for easy navigation
- Folder tree view for quick access
- Grid and list view options

### ✅ Integration
- Link files to Materials, POs, Deliveries, Payments
- Auto-organize files by project/record type
- Quick upload from within each page
- View all project files in one place

---

## 🔧 Prerequisites

### 1. Windows SMB Server
You need a Windows file server (or Samba server) accessible on your office network.

**Supported:**
- Windows Server 2012+ with File Services
- Windows 10/11 with file sharing enabled
- Samba server (Linux/NAS)

### 2. Network Configuration
- Server must be accessible from the machine running Flask dashboard
- Ports: 445 (SMB over TCP/IP)
- Optional: 139 (NetBIOS)

### 3. User Credentials
- Username and password with read/write access to the share
- Domain name (if using Active Directory) or WORKGROUP for standalone

---

## 📋 Step-by-Step Setup

### Step 1: Prepare SMB Server

#### Windows Server Setup:

1. **Create Share:**
   ```
   - Open File Explorer → Navigate to folder to share
   - Right-click → Properties → Sharing → Advanced Sharing
   - Check "Share this folder"
   - Share name: "Projects" (or your preferred name)
   - Click Permissions → Add your user → Grant Full Control
   ```

2. **Note Server Information:**
   ```
   Server Name: FILE-SERVER (Computer name)
   Server IP: 192.168.1.100 (ipconfig to find)
   Share Name: Projects
   Domain: WORKGROUP or your domain
   ```

3. **Create Base Folder:**
   ```
   Inside the share, create:
   Projects\
   └── PKP_Projects\
       └── (dashboard will create subfolders here)
   ```

#### Test Access from Command Line:
```cmd
net use \\192.168.1.100\Projects /user:admin password
dir \\192.168.1.100\Projects\PKP_Projects
```

If this works, you're ready to proceed!

---

### Step 2: Install Python SMB Library

The dashboard uses `pysmb` library for SMB connections.

#### On WSL (Required per project rules):

```bash
wsl bash -c "cd '/mnt/c/.../9. material delivery dashboard' && source venv/bin/activate && pip install pysmb"
```

**Verify installation:**
```bash
python -c "from smb.SMBConnection import SMBConnection; print('✅ pysmb installed')"
```

---

### Step 3: Configure Dashboard

#### Edit `.env` file:

Copy `.env.example` to `.env` if you haven't already:
```bash
cp .env.example .env
```

Add SMB configuration at the end of `.env`:

```bash
# SMB/CIFS File Server Configuration
SMB_SERVER_IP=192.168.1.100          # Your server IP address
SMB_SERVER_NAME=FILE-SERVER          # Your server computer name
SMB_SHARE_NAME=Projects              # Share name you created
SMB_USERNAME=admin                   # Username with access
SMB_PASSWORD=your-secure-password    # User's password
SMB_DOMAIN=WORKGROUP                 # Domain or WORKGROUP
SMB_CLIENT_NAME=PKP-Dashboard        # Client identifier
SMB_BASE_PATH=PKP_Projects           # Base folder inside share
```

**Example for Active Directory domain:**
```bash
SMB_DOMAIN=COMPANY                   # Your AD domain
SMB_USERNAME=john.doe                # Domain user
SMB_PASSWORD=SecurePass123!
```

---

### Step 4: Test Connection

1. **Start Flask dashboard:**
   ```bash
   wsl bash -c "cd '/mnt/c/.../9. material delivery dashboard' && source venv/bin/activate && python app.py"
   ```

2. **Navigate to Files page:**
   ```
   http://localhost:5001/files
   ```

3. **Click "Test Connection" button**
   
   **Expected result:**
   ```
   ✅ Connected to SMB Server
   Server: FILE-SERVER (192.168.1.100) | Share: Projects | Folders: 0
   ```

4. **If connection fails**, check:
   - Server IP is correct and pingable: `ping 192.168.1.100`
   - Share is accessible: `net use \\192.168.1.100\Projects`
   - Username/password are correct
   - Firewall allows port 445
   - SMB version compatibility (see Troubleshooting)

---

## 🚀 Usage Guide

### Browse Files

1. Navigate to **Files** in the main menu
2. See folder tree on left, files on right
3. Click folders to navigate
4. Use breadcrumbs to go back

### Upload Files

1. Click **Upload Files** button
2. **Drag and drop** files OR click **Browse Files**
3. Select multiple files (Ctrl+Click)
4. Files upload to current folder
5. Progress bar shows upload status

### Download Files

1. Click **Download** button on any file
2. File downloads to your Downloads folder
3. Multiple downloads: Click each file's download button

### Create Folders

1. Click **New Folder** button
2. Enter folder name (e.g., "Villa_123")
3. Click **Create**
4. New folder appears in current location

### Delete Files

1. Click **Delete** button (red trash icon)
2. Confirm deletion in popup
3. File is permanently removed from server

### Search Files

1. Type in search box (top right)
2. Results filter in real-time
3. Clear search to see all files

---

## 📁 Recommended Folder Structure

Organize your projects like this:

```
PKP_Projects/
├── Villa_Projects/
│   ├── Villa_123/
│   │   ├── PO_Documents/
│   │   │   ├── PO_001_Steel.pdf
│   │   │   └── PO_002_Electrical.pdf
│   │   ├── Delivery_Notes/
│   │   │   └── DN_20250110_DB.pdf
│   │   ├── Invoices/
│   │   │   └── INV_2025_001.pdf
│   │   └── Material_Submittals/
│   │       └── DB_Technical_Sheet.pdf
│   └── Villa_456/
│       └── ...
├── Commercial_Projects/
│   └── ...
└── Warehouse_Documents/
    └── ...
```

**Benefits:**
- Easy to find project documents
- Consistent organization across projects
- Supports audit trails
- Integrates with dashboard records

---

## 🔒 Security Best Practices

### 1. User Permissions
```
✅ DO: Create dedicated SMB user for dashboard
✅ DO: Grant only necessary permissions (read/write to PKP_Projects)
❌ DON'T: Use administrator account
❌ DON'T: Grant access to system folders
```

### 2. Network Security
```
✅ DO: Keep SMB server on internal network only
✅ DO: Use strong passwords (12+ characters)
✅ DO: Enable SMB encryption if available
❌ DON'T: Expose SMB port (445) to internet
❌ DON'T: Use default passwords
```

### 3. Backup
```
✅ DO: Regular backups of PKP_Projects folder
✅ DO: Test restore procedures
✅ DO: Keep backup off-site
```

---

## 🐛 Troubleshooting

### Connection Failed

**Error:** `Failed to connect to SMB server`

**Solutions:**
1. **Check network:**
   ```bash
   ping 192.168.1.100
   ```
   If fails: Check server is on, cables connected

2. **Test SMB access:**
   ```cmd
   net use \\192.168.1.100\Projects /user:admin password
   ```
   If fails: Username/password wrong OR share doesn't exist

3. **Check firewall:**
   ```powershell
   # Allow SMB in Windows Firewall (on server)
   netsh advfirewall firewall add rule name="SMB In" dir=in action=allow protocol=TCP localport=445
   ```

4. **Enable SMB on server:**
   ```powershell
   # Check if SMB is enabled
   Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
   
   # Enable if needed (SMB2/3 preferred)
   Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -All
   ```

### Authentication Failed

**Error:** `STATUS_LOGON_FAILURE` or `Access Denied`

**Solutions:**
1. Verify credentials in `.env`
2. Check username format:
   - Standalone: `admin`
   - Domain: `DOMAIN\username` or just `username` if domain set correctly
3. Test login on server directly
4. Reset user password

### Permission Denied

**Error:** `Permission denied` when uploading/creating folders

**Solutions:**
1. Check user has **Full Control** on share
2. Check NTFS permissions on folder (right-click → Properties → Security)
3. Grant "Modify" permissions to your user

### Files Not Appearing

**Solutions:**
1. Click **Refresh** button
2. Check you're in correct folder (breadcrumb)
3. Verify files exist on server directly
4. Check file permissions

### Slow Performance

**Solutions:**
1. Check network speed (should be 100Mbps+ on LAN)
2. Reduce max_depth for folder tree (default: 3)
3. Use wired connection instead of Wi-Fi
4. Check server disk I/O

### SMB Version Mismatch

**Error:** `Protocol negotiation failed`

**Solutions:**
1. Dashboard uses SMBv2/v3 by default
2. If server only supports SMBv1 (not recommended for security):
   ```python
   # In services/smb_service.py, add:
   use_ntlm_v2=True  # Already set
   ```
3. Upgrade server to support SMBv2+

---

## 🔧 Advanced Configuration

### Connection Pooling

For better performance with multiple users:

```python
# services/smb_service.py - Add connection pool
from queue import Queue

class SMBConnectionPool:
    def __init__(self, max_connections=5):
        self.pool = Queue(maxsize=max_connections)
        # Create connections
    
    def get_connection(self):
        # Return available connection
    
    def release_connection(self, conn):
        # Return to pool
```

### Automatic Folder Creation

Automatically create project folders when creating PO:

```python
# When creating PO record
project_name = f"Villa_{po_number}"
smb_service.create_folder('Villa_Projects', project_name)
smb_service.create_folder(f'Villa_Projects/{project_name}', 'PO_Documents')
smb_service.create_folder(f'Villa_Projects/{project_name}', 'Delivery_Notes')
# etc.
```

### File Linking

Link uploaded files to database records:

```python
# In models/purchase_order.py add:
smb_file_path = db.Column(db.String(500))  # Store path to file on SMB

# When uploading from PO page:
po.smb_file_path = f"Villa_Projects/Villa_{po.po_number}/PO_Documents/{filename}"
```

---

## 📊 Monitoring & Logs

### Check Connection Status

```python
# In Python console
from services.smb_service import smb_service
result = smb_service.test_connection()
print(result)
```

### View Logs

Dashboard logs SMB operations:

```bash
# Check Flask logs
tail -f logs/flask.log

# Look for:
✅ Connected to SMB server: FILE-SERVER (192.168.1.100)
✅ Uploaded 15234 bytes to PKP_Projects/Villa_123/PO_001.pdf
❌ SMB connection failed: timeout
```

---

## 🎯 Next Steps

Once basic setup works:

1. **Create project structure** on server
2. **Upload test files** to verify
3. **Train users** on file browser
4. **Set up backups** for PKP_Projects folder
5. **Monitor usage** and performance
6. **Implement file linking** to dashboard records (Phase 6.3)

---

## 📞 Support

### Common Issues
- Most issues: Network connectivity or credentials
- Test with `net use` command first
- Check Windows Event Viewer on server for errors

### Need Help?
1. Review this guide completely
2. Check troubleshooting section
3. Test connectivity with `net use`
4. Verify `.env` configuration
5. Check Flask logs for errors

---

## ✅ Checklist

Before going live:

- [ ] SMB server accessible on network
- [ ] Share created with proper permissions
- [ ] User account with read/write access
- [ ] pysmb library installed (`pip install pysmb`)
- [ ] `.env` configured with correct credentials
- [ ] Test Connection succeeds in dashboard
- [ ] Can upload files successfully
- [ ] Can download files successfully
- [ ] Folder structure created
- [ ] Backups configured
- [ ] Users trained on interface

---

**Version:** 1.0  
**Last Updated:** October 10, 2025  
**Phase:** 6 - SMB File Server Integration
