# realme-debloater

A simple command-line tool for checking and carefully removing unwanted preinstalled apps from Realme phones.

**No root. No bootloader unlocking. No GUI.** You only need a computer, a USB cable, Python and Android's ADB tools.

> **Made for beginners:** Follow the setup steps in order. You do not need to know Android commands or Python programming to use this tool.

## What does this tool do?

- Checks whether your phone is connected correctly.
- Shows the apps and packages installed on your phone.
- Searches for a package by name.
- Shows basic information about a package.
- Lets you manually approve a package before removal.
- Starts with a preview, and only makes a change after extra confirmation.
- Keeps a record of packages removed by this tool so you can try to restore them.

The initial device profile is **Realme 8 5G (RMX3241), Android 13, Realme UI 4.0**. The tool can inspect other Android/Realme devices too, but package behaviour differs by model, region, Android version and firmware.

## Before you start

You need:

1. A Windows, macOS or Linux computer.
2. A USB cable that supports data transfer (some cables only charge).
3. An internet connection for the initial setup.
4. Python 3.9 or newer.
5. Android Platform Tools, which provide the `adb` command.
6. Git, if you want to download the project using `git clone`.

**You do not need to install Python libraries.** The script uses Python's built-in modules.

## Step 1: Install the required tools

### Install Python

Download Python 3.9 or newer from the official website:

- https://www.python.org/downloads/

On Windows, during installation, tick **Add Python to PATH** if that option appears.

To check that Python is installed, open Terminal (macOS/Linux) or Command Prompt / PowerShell (Windows) and run:

**macOS / Linux:**

```bash
python3 --version
```

**Windows:**

```powershell
py --version
```

You should see a version number such as `Python 3.12.0`. If the command is not recognised, Python is not installed correctly or is not on your PATH.

### Install ADB (Android Platform Tools)

ADB lets your computer communicate with your Android phone.

**macOS with Homebrew:**

```bash
brew install android-platform-tools
```

**Windows:**

1. Download **SDK Platform-Tools for Windows** from https://developer.android.com/tools/releases/platform-tools.
2. Extract the downloaded ZIP file.
3. Open the extracted `platform-tools` folder.
4. Click the address bar in File Explorer, type `cmd`, and press Enter. This opens Command Prompt in that folder.
5. Run `adb version` to check that it works.

Keep this Command Prompt window open for the next steps, or add the `platform-tools` folder to your Windows PATH so `adb` works from any folder.

**Linux (Ubuntu / Debian):**

```bash
sudo apt update
sudo apt install adb
```

For other Linux distributions, install Android Platform Tools using your distribution's package manager or the official download page above.

Check ADB installation:

```bash
adb version
```

If your computer says `adb: command not found` or that `adb` is not recognised, ADB is not installed or is not on your PATH yet.

### Install Git (only if you are using git clone)

- Windows: https://git-scm.com/download/win
- macOS: install Xcode Command Line Tools with `xcode-select --install`, or install Git using your preferred package manager.
- Linux: install `git` through your distribution's package manager.

You can skip Git if you download the project as a ZIP instead.

## Step 2: Download this project

Choose **one** of these methods.

### Option A: Download with Git (recommended)

Open Terminal, Command Prompt or PowerShell and run:

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/realme-debloater.git
cd realme-debloater
```

Replace `YOUR-GITHUB-USERNAME` with the GitHub account or organisation that hosts this repository. For example, the final URL should look like `https://github.com/account-name/realme-debloater.git`.

> If the repository is private, you must be signed in to GitHub and have permission to access it.

### Option B: Download as a ZIP (no Git required)

1. Open this project's GitHub page.
2. Click the green **Code** button.
3. Select **Download ZIP**.
4. Extract the ZIP file.
5. Open a terminal inside the extracted `realme-debloater` folder.

The terminal must be opened in the project folder. If you run the commands from a different folder, Python may not find the script or its configuration files.

## Step 3: Prepare your Realme phone

The steps below enable ADB access. They do **not** root the phone or unlock its bootloader.

1. Open **Settings** on your phone.
2. Open **About device** (the name may differ slightly by Realme UI version).
3. Find **Version** or **Build number**.
4. Tap the build number seven times. Enter your phone PIN/password if requested. You should see a message that Developer options are enabled.
5. Return to Settings and open **Additional settings → Developer options**. On some versions, Developer options may appear in a different Settings section.
6. Turn on **USB debugging**.
7. Connect the phone to your computer using the USB cable.
8. Unlock your phone. When the **Allow USB debugging?** message appears, check the RSA fingerprint prompt and tap **Allow**. Only approve a computer you trust.

If the permission prompt does not appear, unplug and reconnect the phone, keep it unlocked, and check that USB debugging is enabled.

## Step 4: Check the connection

In your terminal, run:

```bash
adb devices
```

The output should show your phone's serial number followed by the word `device`, for example:

```text
List of devices attached
ABC1234567    device
```

If it says `unauthorized`, unlock your phone and accept the USB debugging prompt. If no device appears, check the cable, USB port, USB debugging setting and (on Windows) USB drivers.

## Step 5: Run realme-debloater

Use the command for your computer's operating system.

**macOS / Linux:**

```bash
python3 src/realme_debloater.py doctor
```

**Windows:**

```powershell
py src\realme_debloater.py doctor
```

This checks the ADB connection and displays basic information about the connected phone. It does not change anything.

If the check succeeds, scan your phone.

**macOS / Linux:**

```bash
python3 src/realme_debloater.py scan
```

**Windows:**

```powershell
py src\realme_debloater.py scan
```

The scan creates a timestamped package inventory in the `state` folder. It is a read-only scan: no apps are removed or disabled.

## Useful commands

Run these from inside the `realme-debloater` project folder.

| What you want to do | macOS / Linux | Windows |
|---|---|---|
| Check phone connection | `python3 src/realme_debloater.py doctor` | `py src\realme_debloater.py doctor` |
| Scan installed packages | `python3 src/realme_debloater.py scan` | `py src\realme_debloater.py scan` |
| List all packages | `python3 src/realme_debloater.py list` | `py src\realme_debloater.py list` |
| List downloaded/third-party apps | `python3 src/realme_debloater.py list --third-party` | `py src\realme_debloater.py list --third-party` |
| Search package names | `python3 src/realme_debloater.py search heytap` | `py src\realme_debloater.py search heytap` |
| Inspect a package | `python3 src/realme_debloater.py info com.heytap.market` | `py src\realme_debloater.py info com.heytap.market` |

Replace `heytap` or `com.heytap.market` with the search term or package name you want to inspect.

## Removing an app (read this carefully)

**Do not remove a package just because its name looks unfamiliar.** Some packages that look unnecessary are responsible for calls, mobile data, security, updates, permissions or basic phone functions.

The tool does not come with a list of packages that are automatically approved for deletion. You must research and approve a package yourself.

### 1. Find the package name

For example, search for a package containing `heytap`:

```bash
python3 src/realme_debloater.py search heytap
```

On Windows, use `py` instead of `python3` and Windows-style path separators as shown above.

### 2. Inspect it

```bash
python3 src/realme_debloater.py info PACKAGE.NAME
```

Replace `PACKAGE.NAME` with the exact package name. Research what it does for your exact phone model and firmware before continuing. The tool's information output is not proof that a package is safe to remove.

### 3. Approve it locally

Only after you have verified that the package is optional, run:

```bash
python3 src/realme_debloater.py approve PACKAGE.NAME --reason "Why I verified this is optional"
```

The tool will ask you to type `APPROVE`. This only adds the package to your local approval list. **It does not uninstall the app.**

### 4. Preview the removal

```bash
python3 src/realme_debloater.py remove PACKAGE.NAME
```

This is a dry run. It shows the command that would be executed and does not change your phone.

### 5. Apply the removal

Only if you are certain, run:

```bash
python3 src/realme_debloater.py remove PACKAGE.NAME --apply
```

The tool will ask you to type the exact package name again. This is an extra safety check, not an invitation to guess.

### What does removal actually do?

The tool uses Android's `pm uninstall --user 0` command. This removes the app for the phone's primary user. It does **not** erase the app's system image from the firmware partition, and it is not the same as deleting the firmware or permanently removing the system component.

## Restoring an app

If you removed a package using this tool, it records the change in `state/changes.json`. To preview restoration:

```bash
python3 src/realme_debloater.py restore PACKAGE.NAME
```

To apply restoration:

```bash
python3 src/realme_debloater.py restore PACKAGE.NAME --apply
```

Restoration uses Android's `cmd package install-existing` command. It may not restore the app's old data, preferences or updates. If the phone is malfunctioning, do not keep removing packages to see what happens. That is how a simple cleanup becomes an afternoon of regret.

## Safety rules

- No root access, bootloader unlocking, flashing or recovery modifications are required.
- `doctor`, `scan`, `list`, `search` and `info` are intended for inspection and do not remove packages.
- The approval list starts empty.
- Removal is a dry run unless you add `--apply`.
- Applying a removal requires typing the exact package name.
- Core Android packages and known Realme/OPPO update components are protected by the script.
- Do not remove security, telephony, Settings, launcher, permission, Google Play services, updater, OTA, ROM update or device-specific framework packages.
- Back up important files before changing packages.
- Do not assume a package is safe on every Realme model just because someone removed it successfully on another model.

**Important:** The initial RMX3241 inventory included `com.oplus.ota`, `com.oplus.sau`, `com.oplus.sauhelper`, `com.oplus.romupdate` and `com.oplus.cota`. These components are deliberately protected. Their presence does not mean an OTA update file is taking up storage.

## Project structure

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

## Troubleshooting

**`adb` is not recognised / command not found**

Install Android Platform Tools and make sure the `adb` command is available in your terminal. On Windows, you can run commands from inside the extracted `platform-tools` folder if you have not added it to PATH.

**`unauthorized` appears next to my phone**

Unlock the phone and accept the USB debugging permission prompt. You can also disconnect and reconnect the cable to make the prompt appear again.

**No device appears after running `adb devices`**

Try another USB cable or port, make sure the cable supports data, enable USB debugging, and check Windows USB drivers if applicable.

**The script says it expected exactly one authorized device**

The tool currently works with one connected, authorized phone at a time. Disconnect other Android devices or emulators, then run `adb devices` again.

**Python is not recognised**

Install Python 3.9 or newer. On Windows, try `py` instead of `python`; on macOS/Linux, try `python3`.

## Contributing

When documenting a package, include its package name, app/component name, purpose, evidence/source, tested device model, firmware build, risk level and restoration method. Never mark a package safe based only on its name. Device-specific testing and credible sources matter.

## Disclaimer

This is an independent community project, not an official Realme or OPPO tool. Use it at your own risk. Back up important data first. OEM updates can change package dependencies and behaviour. The authors are not responsible for data loss, device instability or problems caused by removing packages.
