---
title: Fix Laggy SSH Terminal Sessions on Raspberry Pi Zero 2 W
image: raspberry-pi
tags:
- Raspberry Pi
- SSH
- Troubleshooting
- WiFi
---
## Description

This guide documents a practical fix for slow or laggy SSH terminal sessions on a Raspberry Pi Zero 2 W.

In this case, CPU throttling was not the issue, but WiFi behavior and SSH connection setup overhead were.

## Requirements

- Raspberry Pi Zero 2 W running Raspberry Pi OS
- SSH access to the Pi
- `sudo` access on the Pi
- Access to your client machine's `~/.ssh/config`

## Diagnostics

### Check for CPU throttling

`vcgencmd get_throttled`

Expected healthy output:

`throttled=0x0`

### Check for WiFi firmware warnings

`dmesg -T | egrep -i "brcmfmac|clm_blob|failed with error -2"`

A problematic output looks like:

`Direct firmware load for brcm/brcmfmac43436s-sdio.clm_blob failed with error -2`

### Check WiFi power saving status

`/sbin/iw dev wlan0 get power_save`

## Fixes Applied

### 1. Add missing CLM blob symlink for Zero 2 W WiFi firmware

If the file is missing:

`/lib/firmware/brcm/brcmfmac43436s-sdio.clm_blob`

Create a symlink to the available CLM blob:

`sudo ln -s brcmfmac43436-sdio.clm_blob /lib/firmware/brcm/brcmfmac43436s-sdio.clm_blob`

### 2. Disable WiFi power saving persistently

Install `iw` if needed:

`sudo apt-get update && sudo apt-get install -y iw`

Create a systemd unit at `/etc/systemd/system/wifi-powersave-off.service`:

```ini
[Unit]
Description=Disable WiFi power saving on wlan0
After=network-pre.target
Wants=network-pre.target

[Service]
Type=oneshot
ExecStart=/sbin/iw dev wlan0 set power_save off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

`sudo systemctl daemon-reload && sudo systemctl enable --now wifi-powersave-off.service`

Confirm:

- `/sbin/iw dev wlan0 get power_save` should show `Power save: off`
- `systemctl status wifi-powersave-off.service`

### 3. Speed up repeated SSH sessions from your client machine

Add host settings to `~/.ssh/config` on your workstation:

```sshconfig
Host gideon
  HostName gideon
  User anthony
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 10m
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

This enables SSH connection multiplexing. The first connection stays normal, but additional terminal sessions reuse the existing secure connection and open much faster.

## Results

Observed behavior after applying the changes:

- SSH latency became more consistent
- New terminal sessions were significantly faster after the first connection
- WiFi power save was confirmed as off across reboots (via systemd service)

## Notes

- Reboot the Pi once after adding the firmware symlink to ensure the corrected firmware path is used at boot.
- If sessions are still laggy, test Ethernet or move the Pi closer to the access point to rule out WiFi signal and interference issues.
