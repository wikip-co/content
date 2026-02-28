---
title: Installing Cursor from an AppImage (on Ubuntu)
image: cursor
tags:
- Artificial Intelligence
- Code Editors
- Text Editors
- Development Environments
---
## Description

This article explains how to download and configure the cursor.AppImage on your Debian based system.

## Installation

### Setup Instructions for Ubuntu

0. **Download the latest AppImage**:
- Go to https://www.cursor.com/changelog
  - Click the Download button at the top-right of the page.
  - This will get you a file that looks like this: `cursor-0.44.9-build-2412268nc6pfzgo-x86_64.AppImage`
  - For the purposes of the following instructions, we have renamed the file to `cursor.AppImage`

1. **Extract the AppImage**:
   ```bash
   ./cursor.AppImage --appimage-extract
   ```
   This creates a directory named `squashfs-root` (or similar).

2. **Fix permissions**:
   ```bash
   sudo chown root:root squashfs-root/chrome-sandbox
   sudo chmod 4755 squashfs-root/chrome-sandbox
   ```

3. **Run from the extracted folder to ensure it launches properly**:
   ```bash
   ./squashfs-root/AppRun
   ```

4. Move the Extracted Folder to a Permanent Location

By default, the folder is named `squashfs-root`. Rename it and place it in `/opt/` (a common location for third-party apps).

```bash
sudo mv squashfs-root /opt/cursor
```
5. Make It Launchable by Typing `cursor` in the Terminal

Create a **symbolic link** in `/usr/local/bin/` pointing to the `AppRun` file. This way, when you type `cursor`, the system will launch the application.

```bash
sudo ln -s /opt/cursor/AppRun /usr/local/bin/cursor
```

Now, if you open a new terminal (or re-source your shell), you should be able to type:
```bash
cursor
```
and it will launch the app.

6. Create a Desktop Entry (so it appears in the Applications menu)

**Create a .desktop file** in your local applications directory:
   ```bash
   nano ~/.local/share/applications/cursor.desktop
   ```
**Paste the following** (modify `Name`/`Icon` if desired):

```ini
[Desktop Entry]
Name=Cursor
Exec=/opt/cursor/AppRun
Terminal=false
Type=Application
Icon=/opt/cursor/cursor.png
StartupWMClass=Cursor
X-AppImage-Version=2412268nc6pfzgo
Comment=Cursor is an AI-first coding environment.
MimeType=x-scheme-handler/cursor;
Categories=Utility;
```
**Save** (`Ctrl+O`, `Enter`), then **exit** (`Ctrl+X`).

**Make the .desktop file executable** (this step is sometimes optional, but it’s good practice):
   ```bash
   chmod +x ~/.local/share/applications/cursor.desktop
   ```

Within a few moments, you should see “Cursor” appear in the Ubuntu/GNOME application launcher or “Show Applications” overview.

(Optional) Validate the Desktop File

You can run:
```bash
desktop-file-validate ~/.local/share/applications/cursor.desktop
```
to ensure there are no syntax errors.

If you do **not** see the new entry right away:
- Log out and log back in, or  
- Run:
  ```bash
  update-desktop-database ~/.local/share/applications/
  ```
  on some systems to refresh the menu.

- **Launch from Terminal**: Just type `cursor`  
- **Launch from Applications menu**: Look for “Cursor” (or whatever `Name=` you set in the `.desktop` file)
