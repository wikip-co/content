---
title: Connecting to an Android Phone with a Local scrcpy Build
image: devops
tags:
- Android
- ADB
- scrcpy
- Remote Access
- Linux
---
## Description

This article explains how to build and run scrcpy from a local source checkout on Linux, connect to an Android phone over USB, and fall back to Android's wireless debugging connection when USB is unreliable. Scrcpy mirrors the phone's video and audio and accepts keyboard and mouse input without requiring root access or an app installed on the phone.[^1]

The commands were tested with scrcpy 4.0, a Pixel 7 Pro running Android 16, and an Ubuntu-based Linux host. Replace the example device serial, IP address, and ports with values reported by your own phone and `adb`.

## Prerequisites

### Linux host

The host needs:

- A data-capable USB cable for the initial USB connection
- Git and `curl`
- Android Debug Bridge (`adb`)
- Meson and Ninja
- SDL 3, FFmpeg, libusb, and their development packages
- A graphical Linux session in which scrcpy can open a window
- The same local network as the phone when using wireless debugging

On Debian or Ubuntu, install the runtime and client build dependencies documented by scrcpy:[^2]

```bash
sudo apt update
sudo apt install curl ffmpeg libsdl3-0 adb libusb-1.0-0 \
  gcc git pkg-config meson ninja-build libsdl3-dev \
  libavcodec-dev libavdevice-dev libavformat-dev libavutil-dev \
  libswresample-dev libusb-1.0-0-dev libv4l-dev
```

This guide uses scrcpy's prebuilt Android server, so Java and a full Android SDK are not required. They are required if the server is built from source.

### Android phone

Scrcpy supports Android 5.0/API 21 or newer. Enable developer options and USB debugging before connecting:[^1][^4]

1. Open **Settings → About phone**.
2. Tap **Build number** seven times.
3. Open **Settings → System → Developer options**.
4. Enable **USB debugging**.
5. Connect the phone with a data-capable USB cable.
6. Unlock the phone and accept the RSA debugging authorization prompt. Select **Always allow from this computer** only if the host is trusted.

For a wireless connection on Android 11 or newer, also enable **Wireless debugging** under developer options. The phone and host must be able to reach each other over the local network.[^3][^5]

## Build scrcpy from the Local Checkout

### Clone and select a release

Use the official repository and select an exact release so that the client and Android server versions are predictable:

```bash
mkdir -p "$HOME/Workspace"
cd "$HOME/Workspace"
git clone https://github.com/Genymobile/scrcpy.git
cd scrcpy
git switch --detach v4.0
git describe --tags --exact-match
```

For an existing checkout:

```bash
cd "$HOME/Workspace/scrcpy"
git fetch --tags origin
git switch --detach v4.0
```

The remaining examples are pinned to v4.0. When upgrading, replace the tag, download URL, and checksum with the values in the new release's `doc/build.md`.

### Download and verify the matching server

The host client uploads a small server program to the phone at startup. The server version must exactly match the client version.[^2]

```bash
curl -fL \
  -o scrcpy-server \
  https://github.com/Genymobile/scrcpy/releases/download/v4.0/scrcpy-server-v4.0

printf '%s  %s\n' \
  '84924bd564a1eb6089c872c7521f968058977f91f5ff02514a8c74aff3210f3a' \
  'scrcpy-server' | sha256sum --check
```

The verification command must print:

```text
scrcpy-server: OK
```

Do not continue if the checksum does not match.

### Configure and compile

Create a release build that copies the verified server into the build directory:

```bash
meson setup build-auto \
  --buildtype=release \
  --strip \
  -Db_lto=true \
  -Dprebuilt_server="$PWD/scrcpy-server"

ninja -C build-auto
```

If `build-auto` already exists, reconfigure it before rebuilding:

```bash
meson setup --reconfigure build-auto \
  -Dprebuilt_server="$PWD/scrcpy-server"
ninja -C build-auto
```

Confirm that the copied server still has the expected checksum:

```bash
sha256sum build-auto/server/scrcpy-server
```

The local launcher syntax is important: `./run` takes the build directory as its first argument, followed by normal scrcpy options.

## Connect over USB

Start or refresh ADB and list its devices:

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

- `unauthorized` means the phone needs to be unlocked and the RSA prompt accepted.
- An empty list means ADB cannot currently communicate with the phone. Reconnect the cable, try a direct host USB port, and restart ADB.
- `offline` usually requires reconnecting the phone or restarting ADB.

Launch the build and explicitly select the USB serial shown by `adb devices -l`:

```bash
cd "$HOME/Workspace/scrcpy"
./run build-auto --serial DEVICE_SERIAL
```

If only one ADB device is present, this shorter selector also works:

```bash
./run build-auto --select-usb
```

Keep the terminal process running while using the scrcpy window. Closing the window stops scrcpy.

## Connect with Android Wireless Debugging

Wireless debugging is useful when the USB controller, cable, or composite MTP/ADB connection resets during transfer. It is also convenient after the host has been paired once.

### Pair the host once

On the phone, open **Settings → System → Developer options → Wireless debugging**, then select **Pair device with pairing code**. The pairing screen shows a pairing IP address and port plus a six-digit code.

On the host, run:

```bash
adb pair PHONE_IP:PAIRING_PORT
```

Enter the six-digit code when prompted. The pairing port is temporary and is not normally the same port used by `adb connect`.[^5]

### Connect to the debugging endpoint

Return to the main **Wireless debugging** screen. Use the **IP address & port** value shown there:

```bash
adb connect PHONE_IP:DEBUG_PORT
adb devices -l
```

For example:

```text
List of devices attached
DEVICE_SERIAL             device usb:4-2 product:cheetah model:Pixel_7_Pro
192.168.1.50:37853        device product:cheetah model:Pixel_7_Pro
```

When both USB and TCP/IP transports are listed, select the TCP/IP serial explicitly:[^3]

```bash
cd "$HOME/Workspace/scrcpy"
./run build-auto --serial PHONE_IP:DEBUG_PORT
```

The successful startup log should identify the phone and then report the renderer and video texture, for example:

```text
[server] INFO: Device: [Google] google Pixel 7 Pro (Android 16)
INFO: Renderer: opengl
INFO: Texture: 1440x3120
```

The wireless debugging port may change after wireless debugging, Wi-Fi, or the phone is restarted. Read the current endpoint from the phone instead of assuming that an old port is still valid.

Disconnect when finished:

```bash
adb disconnect PHONE_IP:DEBUG_PORT
```

Disable wireless debugging on the phone when it is not needed, especially on an untrusted network.

## Troubleshooting

| Symptom | Likely cause | Corrective action |
| --- | --- | --- |
| `adb devices -l` is empty | USB transport did not enumerate or ADB retained stale state | Unlock and reconnect the phone, try another data cable or a direct USB port, then run `adb kill-server && adb start-server`. |
| Device is `unauthorized` | Host key has not been approved | Accept the RSA prompt on the unlocked phone. Revoke USB debugging authorizations in developer options and reconnect if the prompt never appears. |
| `adb push` reports `failed to read copy response` and the device disappears | The USB device reset during the server upload | Replug the phone, change the cable/port, avoid an unstable hub, and use wireless debugging if USB continues resetting. |
| USB repeatedly resets with the standard ADB backend | Host ADB/libusb interaction | As a diagnostic, restart ADB with `adb kill-server`, `ADB_LIBUSB=1 adb start-server`, wait two seconds, and run `adb devices -l` again. This does not repair a bad cable or controller. |
| `The server version (...) does not match the client (...)` | A stale or wrong prebuilt server was copied into the build | Download the server for the exact checked-out scrcpy release, verify its checksum, reconfigure Meson, and rebuild. |
| Meson says the build data was generated by an incompatible version | Meson was upgraded after the build directory was created | Run `meson setup --reconfigure build-auto` and then `ninja -C build-auto`. If reconfiguration cannot recover the directory, create a new build directory name. |
| `adb connect` cannot reach the phone | Wrong endpoint, different network, client isolation, firewall, or VPN routing | Re-read **IP address & port**, confirm both devices are on the same reachable LAN, and temporarily disable a VPN such as WireGuard if it captures or blocks local routes. Pair again if authorization was removed. |
| scrcpy reports more than one device | USB and Wi-Fi transports are both active | Pass `--serial DEVICE_SERIAL` for USB or `--serial PHONE_IP:DEBUG_PORT` for Wi-Fi. |
| Wayland reports that it cannot set the window icon | The compositor lacks the optional icon protocol | Ignore the warning if the scrcpy window and video stream open normally. |

To confirm that Linux itself still sees a phone that ADB does not list, use:

```bash
lsusb | grep -Ei 'Google|Pixel|18d1'
```

If `lsusb` sees the phone but ADB does not, restart ADB after reconnecting the phone. If the kernel repeatedly disconnects and re-enumerates the device during transfers, prefer a direct USB port, another cable, or wireless debugging.

## Repeat-Use Checklist

After the one-time build and pairing steps, a normal wireless session only requires:

```bash
cd "$HOME/Workspace/scrcpy"
adb connect PHONE_IP:DEBUG_PORT
adb devices -l
./run build-auto --serial PHONE_IP:DEBUG_PORT
```

For a normal USB session:

```bash
cd "$HOME/Workspace/scrcpy"
adb devices -l
./run build-auto --serial DEVICE_SERIAL
```

Rebuild whenever the checked-out scrcpy version changes, and always keep the host client and Android server on the same release.

## Sources

[^1]: **Title:** [scrcpy README and prerequisites](https://github.com/Genymobile/scrcpy/blob/v4.0/README.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^2]: **Title:** [Build scrcpy](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/build.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^3]: **Title:** [scrcpy connection documentation](https://github.com/Genymobile/scrcpy/blob/v4.0/doc/connection.md)<br>
**Publication:** [Genymobile/scrcpy](https://github.com/Genymobile/scrcpy)<br>
**Version:** 4.0

[^4]: **Title:** [Configure on-device developer options](https://developer.android.com/studio/debug/dev-options)<br>
**Publication:** [Android Developers](https://developer.android.com/)

[^5]: **Title:** [Android Debug Bridge: Connect to a device over Wi-Fi](https://developer.android.com/tools/adb#wireless-android11-command-line)<br>
**Publication:** [Android Developers](https://developer.android.com/)
