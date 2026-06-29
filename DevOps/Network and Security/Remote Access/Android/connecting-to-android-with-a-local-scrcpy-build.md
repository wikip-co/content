---
title: Installing, Updating, and Using scrcpy from a Local Checkout
image: devops
tags:
- Android
- ADB
- scrcpy
- Remote Access
- Linux
---
## Description

This article explains how scrcpy works, how to install and update the current
release from an official local checkout, and how to connect to an Android device
over USB or Wi-Fi. It also covers common operating modes and the failure caused
when an older scrcpy binary remains linked to FFmpeg libraries that a Linux
upgrade has replaced.

The commands were validated with scrcpy 4.0, a Pixel 7 Pro running Android 16,
and Ubuntu 26.04. Replace release numbers, checksums, device serials, IP
addresses, and ports with the values shown by the current scrcpy release and by
`adb` on the local system.

## How scrcpy Works

Scrcpy is a native host application for Linux, macOS, and Windows. It uses
Android Debug Bridge (ADB) over USB or TCP/IP to start a matching scrcpy server
on the Android device. The server captures encoded video and audio and sends the
streams to the host client, which decodes and displays them. Control messages
travel in the other direction.[^1][^3]

This design has several useful properties:

- The Android device does not need root access.
- No permanent Android app, account, cloud service, or internet connection is
  required.
- Nothing is left installed on the device after the session ends.
- The client and server must come from the same scrcpy version.
- ADB provides the transport, so every ADB device selector and serial also
  applies to scrcpy.

Scrcpy does more than screen mirroring. Version 4.0 supports keyboard, mouse,
gamepad, and clipboard control; audio forwarding on Android 11 or newer;
recording; virtual displays; screen-off operation; Android 12+ camera capture;
Linux V4L2 webcam output; and an OTG control-only mode that does not require USB
debugging.[^1]

## Choose an Installation Method

Use only the official `Genymobile/scrcpy` repository and its release assets.
The project explicitly warns against downloads from similarly named third-party
sites.[^1]

| Method | Best use | Update model | Trade-off |
| --- | --- | --- | --- |
| Official Linux release archive | A self-contained, portable copy with the fewest host-library problems | Download and extract each new release | Does not automatically replace a `scrcpy` command elsewhere on `PATH` |
| Official `install_release.sh` from a local checkout | Regular use from Ubuntu while following new upstream releases | `git pull --ff-only`, then rerun the script | Rebuild after a major distribution or FFmpeg upgrade |
| Distribution package | Maximum package-manager integration | Updated by the distribution | Debian/Ubuntu packages may substantially lag upstream; scrcpy marks them obsolete |
| Full manual source build | Developing or testing scrcpy itself | Reconfigure and rebuild the selected branch | Requires more build tooling and, when building the Android server, a JDK and Android SDK |

For this host, the local-checkout installation is the best balance. It installs
the command, server, manual page, desktop entries, icons, and shell completions
under `/usr/local`, while keeping updates explicit and repeatable.[^2][^3]

## Prerequisites

### Linux host

Install the runtime and client build dependencies documented by scrcpy for
Debian and Ubuntu:[^2]

```bash
sudo apt update
sudo apt install ffmpeg libsdl3-0 libusb-1.0-0 adb wget \
  gcc git pkg-config meson ninja-build libsdl3-dev \
  libavcodec-dev libavdevice-dev libavformat-dev libavutil-dev \
  libswresample-dev libusb-1.0-0-dev libv4l-dev
```

The release installation uses scrcpy's matching, prebuilt Android server. Java
and the Android SDK are therefore unnecessary unless developing the server or
building every component from source.

### Android device

Normal mirroring requires Android 5.0/API 21 or newer. Audio forwarding requires
Android 11 or newer, and camera mirroring requires Android 12 or newer.[^1]

Enable developer options and USB debugging:[^5]

1. Open **Settings -> About phone**.
2. Tap **Build number** seven times.
3. Open **Settings -> System -> Developer options**.
4. Enable **USB debugging**.
5. Connect the phone with a data-capable USB cable.
6. Unlock the phone and accept the RSA debugging authorization prompt.

Select **Always allow from this computer** only on a trusted host. Some Android
vendors also require a separate **USB debugging (Security Settings)** option to
permit keyboard and mouse input.[^1]

For Android 11+ wireless pairing, also enable **Wireless debugging**. The phone
and host must be able to reach each other over the local network.[^6]

## Recommended Installation from the Local Checkout

### Clone the official release branch

Scrcpy's `master` branch tracks the latest release. The `dev` branch contains
work intended for the next release.[^3]

For a new checkout:

```bash
mkdir -p "$HOME/Workspace"
cd "$HOME/Workspace"
git clone https://github.com/Genymobile/scrcpy.git
cd scrcpy
git switch master
git status --short --branch
```

For the existing checkout:

```bash
cd "$HOME/Workspace/scrcpy"
git switch master
git pull --ff-only
git describe --tags --always
```

`--ff-only` prevents an accidental merge commit if local work and upstream have
diverged. Use a separate branch or worktree for scrcpy development rather than
editing the release checkout on `master`.

### Build and install the release

Run the upstream release installer as the normal user:

```bash
cd "$HOME/Workspace/scrcpy"
./install_release.sh
```

The script performs these operations:

1. Downloads the prebuilt Android server for the release recorded in the
   checkout.
2. Verifies the server's SHA-256 checksum.
3. Recreates `build-auto` and builds the native client against the host's
   current libraries.
4. Uses `sudo ninja install` to install the resulting files under `/usr/local`.

Do not run Meson or Ninja themselves as root. Only the final installation step
needs elevated privileges.[^3]

### Verify what will run

Shell command lookup is independent of the current directory. Being inside the
scrcpy repository does not make the shell use the local build when the command
`scrcpy` is entered.

```bash
hash -r
type -a scrcpy
command -v scrcpy
readlink -f "$(command -v scrcpy)"
scrcpy --version
```

For this installation, `command -v` should normally print:

```text
/usr/local/bin/scrcpy
```

Confirm that its shared libraries all resolve:

```bash
ldd "$(command -v scrcpy)" | grep 'not found' || echo 'All libraries resolved'
```

### Run the build without installing it

The repository launcher takes the build directory as its first argument, then
passes all remaining arguments to scrcpy:

```bash
cd "$HOME/Workspace/scrcpy"
./run build-auto --version
./run build-auto
```

This is useful for testing because it explicitly pairs
`build-auto/app/scrcpy` with `build-auto/server/scrcpy-server` and ignores an
older command found on `PATH`.

### Update to a new release

When upstream publishes a release:

```bash
cd "$HOME/Workspace/scrcpy"
git switch master
git status --short --branch
git pull --ff-only
./install_release.sh
hash -r
scrcpy --version
```

Review or commit local modifications before pulling. Also rerun the installer
after a major Ubuntu or FFmpeg upgrade so the client is linked against the new
host library ABI.

### Uninstall the source installation

From the same configured build directory:

```bash
cd "$HOME/Workspace/scrcpy"
sudo ninja -C build-auto uninstall
hash -r
type -a scrcpy
```

This is preferable to manually deleting only `/usr/local/bin/scrcpy`, because
the installation includes the server, manual page, icons, desktop entries, and
shell completions.

## Alternative: Official Portable Linux Release

The official x86_64 release archive includes `scrcpy`, `adb`, the matching
server, the manual page, and artwork. It avoids the FFmpeg mismatch described
later because the release is packaged as a static Linux build.[^2]

For the tested 4.0 release:

```bash
mkdir -p "$HOME/Applications"
cd "$HOME/Applications"

curl -fLO \
  https://github.com/Genymobile/scrcpy/releases/download/v4.0/scrcpy-linux-x86_64-v4.0.tar.gz

printf '%s  %s\n' \
  '7daf05af5d575862e62b068cf6852d6068faf7ef3178f3735e3953e778fbf0ab' \
  'scrcpy-linux-x86_64-v4.0.tar.gz' | sha256sum --check

tar -xzf scrcpy-linux-x86_64-v4.0.tar.gz
cd scrcpy-linux-x86_64-v4.0
./scrcpy --version
./scrcpy
```

Before using these commands for another release, copy its filename and checksum
from the official release page. Do not reuse the 4.0 checksum for another file.

## Connect over USB

Start or refresh ADB and list connected devices:

```bash
adb kill-server
adb start-server
adb devices -l
```

A healthy authorized connection resembles:

```text
List of devices attached
DEVICE_SERIAL    device usb:4-2 product:cheetah model:Pixel_7_Pro
```

The state must be `device`:

- `unauthorized` means the phone must be unlocked and the RSA prompt accepted.
- `offline` usually requires reconnecting the phone or restarting ADB.
- An empty list means ADB cannot communicate with it. Try another data cable, a
  direct host port, and an ADB restart.

If only one device is connected, simply run:

```bash
scrcpy
```

To explicitly select the sole USB device:

```bash
scrcpy --select-usb
```

When multiple devices exist, use the exact serial from `adb devices -l`:

```bash
scrcpy --serial DEVICE_SERIAL
```

Replace `scrcpy` with `./run build-auto` in any example when testing the local
build without installing it.

## Connect over Wi-Fi

Scrcpy uses ADB's network transport. USB and Wi-Fi entries for the same phone
count as separate ADB devices and have different serials.[^4]

### Method 1: Switch an authorized USB device to TCP/IP

With the device connected and authorized over USB, scrcpy can discover its IP,
enable ADB TCP/IP mode, connect, and launch in one command:[^4]

```bash
scrcpy --tcpip
```

Afterward, disconnect USB and select the network device:

```bash
adb devices -l
scrcpy --select-tcpip
```

The traditional manual equivalent is:

```bash
DEVICE_IP=$(adb shell ip route | awk '{print $9; exit}')
adb tcpip 5555
adb connect "$DEVICE_IP:5555"
scrcpy --serial "$DEVICE_IP:5555"
```

This mode generally remains available only until the device or ADB mode is
reset.

### Method 2: Pair with Android 11+ Wireless Debugging

This method can establish ADB without a USB cable after the host is paired.[^6]

1. On the phone, open **Settings -> System -> Developer options -> Wireless
   debugging**.
2. Select **Pair device with pairing code**.
3. Note the pairing IP address, temporary pairing port, and six-digit code.
4. On the host, run:

```bash
adb pair PHONE_IP:PAIRING_PORT
```

Enter the six-digit code. Then return to the main **Wireless debugging** screen
and use its separate **IP address & port** debugging endpoint:

```bash
adb connect PHONE_IP:DEBUG_PORT
adb devices -l
scrcpy --serial PHONE_IP:DEBUG_PORT
```

The pairing port and debugging port are different. The debugging port may
change when Wi-Fi, wireless debugging, or the phone restarts, so read the current
endpoint instead of assuming the previous port remains valid.

Disconnect when finished:

```bash
adb disconnect PHONE_IP:DEBUG_PORT
```

Disable wireless debugging when it is not needed, especially on an untrusted
network.

## Useful Operating Modes

These examples cover the main scrcpy capabilities. Run `scrcpy --help` and use
the linked upstream documentation for all options.

### Improve performance on a high-resolution phone

Reducing resolution usually has the largest impact on latency and reliability:

```bash
scrcpy --max-size=1920 --max-fps=60
scrcpy -m1920 --max-fps=60 --video-codec=h265
```

Use H.264 if the device does not provide a usable H.265 encoder.

### Turn off the physical display while mirroring

```bash
scrcpy --turn-screen-off --stay-awake
```

### Record on the host

```bash
scrcpy --record=session.mkv
scrcpy --no-audio --record=video-only.mp4
scrcpy --no-playback --no-window --record=headless.mkv
```

Scrcpy records the encoded streams directly rather than screen-capturing its
window, so transport jitter does not contaminate the recording timestamps.[^7]

### Use read-only or control-only mode

```bash
scrcpy --no-control
scrcpy --no-video --no-audio --keyboard=uhid --mouse=uhid
```

### Use better keyboard and mouse emulation

```bash
scrcpy --keyboard=uhid --mouse=uhid
```

UHID makes Android treat the host devices more like physical peripherals and
also works over Wi-Fi. Standard SDK input is still the default.

### Capture the Android camera

On Android 12 or newer:

```bash
scrcpy --list-cameras
scrcpy --video-source=camera --camera-facing=front --camera-size=1920x1080
scrcpy --video-source=camera --camera-size=1920x1080 --record=camera.mp4
```

On Linux, camera or display video can also be sent to a configured V4L2
loopback device for OBS or video-conferencing software:[^8]

```bash
scrcpy --video-source=camera --camera-facing=front \
  --v4l2-sink=/dev/video2 --no-video-playback
```

### Start an app in a temporary virtual display

```bash
scrcpy --new-display=1920x1080 --start-app=org.videolan.vlc
scrcpy --new-display --flex-display --keep-active \
  --start-app=com.android.settings
```

The virtual display is destroyed when scrcpy exits unless other options change
that behavior.[^9]

### Control over USB without ADB

OTG mode emulates physical input devices through Android Open Accessory. It
requires USB but not USB debugging. It intentionally provides no video or
audio:[^10]

```bash
scrcpy --otg
scrcpy --otg --gamepad=aoa
```

### Clipboard and file transfer

Clipboard synchronization is enabled by default. Avoid pasting sensitive
content because it becomes available to Android applications through the
Android clipboard. Drag an APK onto the scrcpy window to install it, or drag a
different file to push it to `/sdcard/Download/`.[^11]

## Troubleshooting

### `error while loading shared libraries: libavformat.so.61`

This exact error occurred after the host upgraded to Ubuntu 26.04:

```text
scrcpy: error while loading shared libraries: libavformat.so.61:
cannot open shared object file: No such file or directory
```

The `/usr/local/bin/scrcpy` executable was an older unmanaged build linked to
FFmpeg 7 libraries such as `libavformat.so.61`. Ubuntu now supplied FFmpeg 8
libraries such as `libavformat.so.62`. The local scrcpy 4.0 build was already
correctly linked and ran normally.

Diagnose this class of failure with:

```bash
type -a scrcpy
file "$(command -v scrcpy)"
ldd "$(command -v scrcpy)" | grep -E 'not found|libav(format|codec|util|device)'
```

First confirm that the local build works:

```bash
cd "$HOME/Workspace/scrcpy"
./run build-auto --version
```

Then rebuild and replace the stale installation:

```bash
git switch master
git pull --ff-only
./install_release.sh
hash -r
scrcpy --version
```

If `build-auto` was just built from the current checkout and already works, the
existing build can be installed directly:

```bash
sudo ninja -C build-auto install
hash -r
```

Never create a compatibility symlink such as `libavformat.so.61 ->
libavformat.so.62`. Different SONAME major versions indicate incompatible ABIs;
making the loader accept the wrong library can cause crashes or data corruption.

### Common connection and runtime failures

| Symptom | Likely cause | Corrective action |
| --- | --- | --- |
| `adb devices -l` is empty | USB transport did not enumerate or ADB retained stale state | Unlock and reconnect the phone, try another data cable or direct USB port, then restart ADB. |
| Device is `unauthorized` | Host key has not been approved | Accept the RSA prompt. Revoke USB debugging authorizations and reconnect if the prompt never appears. |
| Device is `offline` | Stale or interrupted ADB transport | Reconnect the device and run `adb kill-server && adb start-server`. |
| `adb push` reports `failed to read copy response` and the device disappears | USB reset during server upload | Change the cable or port, avoid an unstable hub, and use wireless debugging if resets continue. |
| scrcpy reports more than one device | USB and TCP/IP transports are both active | Use `--select-usb`, `--select-tcpip`, or `--serial SERIAL`. |
| Server version does not match client | The local client and Android server came from different releases | Rerun `install_release.sh`, or rebuild with the exact server for the checked-out tag. |
| Meson reports incompatible build data | Meson changed after the build directory was configured | Let `install_release.sh` recreate `build-auto`, or use a new build directory for manual development. |
| `adb connect` cannot reach the phone | Wrong endpoint, different LAN, client isolation, firewall, or VPN route | Re-read the current endpoint, verify LAN reachability, and check firewall/VPN policy. |
| Audio is unavailable | Android is too old or the app/device blocks capture | Audio requires Android 11+. Unlock Android 11 before startup; use `--no-audio` when it is not required. |
| Wayland cannot set the window icon | Compositor lacks an optional icon protocol | Ignore the warning if the video window otherwise works. |

To determine whether Linux still sees a USB phone that ADB does not list:

```bash
lsusb | grep -Ei 'Google|Pixel|18d1'
```

If `lsusb` sees the device but ADB does not, restart ADB after reconnecting it.
Repeated kernel disconnect and re-enumeration events point toward the cable,
port, hub, or USB controller rather than scrcpy.

## Repeat-Use Checklist

Update or repair the installed release:

```bash
cd "$HOME/Workspace/scrcpy"
git switch master
git pull --ff-only
./install_release.sh
scrcpy --version
```

Start a USB session:

```bash
adb devices -l
scrcpy --select-usb
```

Start an already paired wireless session:

```bash
adb connect PHONE_IP:DEBUG_PORT
adb devices -l
scrcpy --serial PHONE_IP:DEBUG_PORT
```

Test the repository build without changing the installed command:

```bash
cd "$HOME/Workspace/scrcpy"
./run build-auto --version
./run build-auto --select-usb
```

## Sources

[^1]: **Title:** [scrcpy README and prerequisites](https://github.com/Genymobile/scrcpy/blob/v4.0/README.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^2]: **Title:** [Install scrcpy on Linux](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/linux.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^3]: **Title:** [Build scrcpy](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/build.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^4]: **Title:** [scrcpy connection documentation](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/connection.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^5]: **Title:** [Configure on-device developer options](https://developer.android.com/studio/debug/dev-options)<br>
**Publication:** [Android Developers](https://developer.android.com/)

[^6]: **Title:** [Android Debug Bridge: Connect to a device over Wi-Fi](https://developer.android.com/tools/adb#wireless-android11-command-line)<br>
**Publication:** [Android Developers](https://developer.android.com/)

[^7]: **Title:** [scrcpy recording documentation](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/recording.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^8]: **Title:** [scrcpy Video4Linux documentation](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/v4l2.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^9]: **Title:** [scrcpy virtual display documentation](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/virtual-display.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^10]: **Title:** [scrcpy OTG documentation](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/otg.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^11]: **Title:** [scrcpy control, clipboard, and file-drop documentation](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/control.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0
