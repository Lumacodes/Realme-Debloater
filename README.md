# realme-debloater

A cautious, non-root ADB toolkit for inspecting and selectively removing unwanted preinstalled Android packages on Realme devices.

**Initial device profile:** Realme 8 5G (RMX3241), Android 13, Realme UI 4.0. The tool is not hard-coded to this model, but package behavior varies by model, region, firmware and carrier.

## Safety first

- No root, bootloader unlock, flashing, or recovery modifications.
- `scan`, `list`, `search`, `info`, and `doctor` are read-only.
- No package is pre-approved for removal. The allow-list starts empty on purpose.
- Removal uses `pm uninstall --user 0`, which removes the app for the primary Android user rather than deleting its system image.
- Removal is dry-run by default. `--apply` and typing the exact package name are both required.
- Core Android packages and known Realme/OPPO OTA components are blocked.
- Successful removals are recorded so the tool can attempt `install-existing` restoration.

**Important:** A package being unfamiliar does not make it bloat. Do not remove security, telephony, settings, launcher, permission, Google Play services, updater, OTA, ROM update, or device-specific framework packages. Restoring a removed package may not restore its data or settings.

## Requirements

- macOS, Linux, or Windows
- Python 3.9+
- Android Platform Tools (`adb`)
- USB debugging enabled on the phone

On macOS with Homebrew:

```bash
brew install android-platform-tools
```

Connect the phone, unlock it, accept the USB debugging prompt, then verify:

```bash
adb devices
```

## Quick start

From this repository directory:

```bash
python3 src/realme_debloater.py doctor
python3 src/realme_debloater.py scan
python3 src/realme_debloater.py list --third-party
python3 src/realme_debloater.py search heytap
python3 src/realme_debloater.py info com.heytap.market
```

`scan` writes a timestamped inventory under `state/`. Review it before making changes.

## Approve and remove a package

Only do this after identifying the package and confirming it is optional for your exact phone and firmware.

```bash
python3 src/realme_debloater.py approve PACKAGE.NAME --reason "Why I verified this is optional"
python3 src/realme_debloater.py remove PACKAGE.NAME
python3 src/realme_debloater.py remove PACKAGE.NAME --apply
```

The first `remove` is a dry run. The second performs the change only after an exact-name confirmation.

## Restore a package

```bash
python3 src/realme_debloater.py restore PACKAGE.NAME
python3 src/realme_debloater.py restore PACKAGE.NAME --apply
```

This uses Android's `cmd package install-existing`. It may not restore app data, preferences, or updates that were cleared separately.

## Current known profile notes

The initial RMX3241 inventory included Realme/OPPO components such as `com.oplus.ota`, `com.oplus.sau`, `com.oplus.sauhelper`, `com.oplus.romupdate`, and `com.oplus.cota`. These are deliberately protected. Their presence does not prove an OTA download is occupying storage.

The tool does not automatically label packages as safe to remove. A package list alone is not enough to establish what a firmware component does. The next step for this device is to build a reviewed package database with evidence for RMX3241 / Android 13 / Realme UI 4.0.

## Project layout

```text
realme-debloater/
├── config/
│   └── approved-packages.json
├── docs/
├── src/
│   └── realme_debloater.py
├── tests/
├── .gitignore
├── LICENSE
└── README.md
```

## Contributing

Package entries should include package name, app/component name, purpose, evidence/source, tested device model, firmware build, risk level, and restore method. Never mark a package safe based only on its name.

## Disclaimer

Use at your own risk. This project is an ADB helper, not an official Realme tool. Back up important data first. OEM updates can change package dependencies and behavior.
