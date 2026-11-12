# Device profile: Realme 8 5G (RMX3241)

Known from the owner's ADB diagnostics:

- Model: Realme 8 5G (RMX3241)
- Android: 13
- UI: Realme UI 4.0
- Build: RMX3241_11_F.11
- SoC: MediaTek MT6833
- Bootloader: locked
- Verified Boot: green
- Root: not enabled

## Known protected package names

- `com.oplus.ota`
- `com.oplus.sau`
- `com.oplus.sauhelper`
- `com.oplus.romupdate`
- `com.oplus.cota`
- `com.google.android.configupdater`

These are updater / ROM update related components. Keep them intact. A package being small or system-installed is not a reason to remove it.

## Package review policy

No other package is pre-approved. Review each candidate against the exact RMX3241 firmware build, test one change at a time, and verify calling, SMS, mobile data, Wi-Fi, Bluetooth, camera, notifications, Play Store, and OTA checking after any change.
