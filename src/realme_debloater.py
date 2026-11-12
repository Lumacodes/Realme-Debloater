#!/usr/bin/env python3
"""A cautious, non-root ADB debloating helper for Realme/Android devices."""
from __future__ import annotations
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "approved-packages.json"
STATE = ROOT / "state"
PACKAGE_RE = re.compile(r"^[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+$")
PROTECTED_EXACT = {
    "android", "com.android.shell", "com.android.systemui", "com.android.settings",
    "com.android.phone", "com.android.providers.settings", "com.android.providers.downloads",
    "com.android.permissioncontroller", "com.google.android.gms", "com.google.android.gsf",
    "com.android.packageinstaller", "com.google.android.packageinstaller",
    "com.oplus.ota", "com.oplus.sau", "com.oplus.sauhelper", "com.oplus.romupdate",
    "com.oplus.cota", "com.google.android.configupdater",
}
PROTECTED_PREFIXES = ("com.android.", "com.google.android.permissioncontroller")


def run_adb(args: list[str], *, check: bool = True) -> str:
    if not shutil.which("adb"):
        raise RuntimeError("ADB was not found. Install Android Platform Tools and ensure `adb` is on PATH.")
    p = subprocess.run(["adb", *args], text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError((p.stderr or p.stdout).strip() or f"adb exited with {p.returncode}")
    return p.stdout.strip()


def require_device() -> str:
    rows = run_adb(["devices"]).splitlines()[1:]
    devices = [r.split()[0] for r in rows if r.strip() and r.split()[-1] == "device"]
    unauthorized = [r for r in rows if r.strip() and r.split()[-1] == "unauthorized"]
    if unauthorized:
        raise RuntimeError("The phone is unauthorized. Unlock it and accept the USB debugging prompt.")
    if len(devices) != 1:
        raise RuntimeError(f"Expected exactly one authorized device; found {len(devices)}. Check `adb devices`.")
    return devices[0]


def packages(third_party: bool = False) -> list[str]:
    args = ["shell", "pm", "list", "packages"]
    if third_party:
        args.append("-3")
    out = run_adb(args)
    return sorted(line.removeprefix("package:").strip() for line in out.splitlines() if line.startswith("package:"))


def load_approved() -> dict:
    if not CONFIG.exists():
        return {"device_profile": "Realme 8 5G RMX3241 / Android 13 / Realme UI 4.0", "approved": []}
    return json.loads(CONFIG.read_text())


def save_approved(data: dict) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(data, indent=2) + "\n")


def load_state() -> dict:
    p = STATE / "changes.json"
    return json.loads(p.read_text()) if p.exists() else {"removed": []}


def save_state(data: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "changes.json").write_text(json.dumps(data, indent=2) + "\n")


def validate_package(name: str) -> None:
    if not PACKAGE_RE.fullmatch(name):
        raise RuntimeError(f"Invalid package name: {name!r}")
    if name in PROTECTED_EXACT or any(name.startswith(p) for p in PROTECTED_PREFIXES):
        raise RuntimeError(f"Refusing to modify protected Android package: {name}")


def cmd_doctor(_: argparse.Namespace) -> None:
    device = require_device()
    print(f"ADB connection: OK ({device})")
    for prop in ("ro.product.manufacturer", "ro.product.model", "ro.build.version.release", "ro.build.version.sdk", "ro.build.display.id"):
        value = run_adb(["shell", "getprop", prop], check=False)
        print(f"{prop}: {value or '(not reported)'}")
    print("\nNo device settings or packages were changed.")


def cmd_scan(args: argparse.Namespace) -> None:
    device = require_device()
    all_pkgs = packages(False)
    third = set(packages(True))
    STATE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    data = {"timestamp_utc": stamp, "device_id": device, "packages": [{"name": p, "kind": "third-party" if p in third else "system"} for p in all_pkgs]}
    out = STATE / f"inventory-{stamp}.json"
    out.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Found {len(all_pkgs)} packages ({len(third)} third-party).")
    print(f"Inventory saved to {out.relative_to(ROOT)}")
    print("Read-only scan complete. Nothing was removed or disabled.")


def cmd_list(args: argparse.Namespace) -> None:
    pkgs = packages(args.third_party)
    for p in pkgs:
        print(p)
    print(f"\n{len(pkgs)} packages")


def cmd_search(args: argparse.Namespace) -> None:
    q = args.query.lower()
    pkgs = packages(False)
    matches = [p for p in pkgs if q in p.lower()]
    print("\n".join(matches) if matches else "No package names matched.")
    print(f"\n{len(matches)} matches")


def cmd_info(args: argparse.Namespace) -> None:
    validate_package(args.package)
    out = run_adb(["shell", "dumpsys", "package", args.package], check=False)
    if not out:
        raise RuntimeError("No package details returned. Check the package name and connection.")
    for line in out.splitlines():
        if any(k in line for k in ("Package [", "codePath=", "resourcePath=", "versionName=", "versionCode=", "userId=", "dataDir=", "firstInstallTime=", "lastUpdateTime=")):
            print(line.strip())


def cmd_approve(args: argparse.Namespace) -> None:
    validate_package(args.package)
    installed = set(packages(False))
    if args.package not in installed:
        raise RuntimeError("That package is not installed on the connected phone.")
    data = load_approved()
    current = {x["name"]: x for x in data.get("approved", [])}
    if args.package in current:
        print("Package is already on the approved list.")
        return
    reason = args.reason.strip()
    if not reason:
        raise RuntimeError("Provide a reason with --reason. Approval is a deliberate manual review step.")
    print(f"Package: {args.package}\nReason: {reason}")
    print("Approval only adds it to your local allow-list. It does not uninstall anything.")
    if input("Type APPROVE to add this package: ").strip() != "APPROVE":
        print("Cancelled.")
        return
    data.setdefault("approved", []).append({"name": args.package, "reason": reason, "approved_at_utc": datetime.now(timezone.utc).isoformat()})
    save_approved(data)
    print("Added to config/approved-packages.json")


def cmd_remove(args: argparse.Namespace) -> None:
    validate_package(args.package)
    data = load_approved()
    approved = {x["name"] for x in data.get("approved", [])}
    if args.package not in approved:
        raise RuntimeError("Package is not approved. Inspect it, then use `approve` with a reason first.")
    installed = set(packages(False))
    if args.package not in installed:
        raise RuntimeError("Package is not currently installed.")
    print("DRY RUN: would run `adb shell pm uninstall --user 0 " + args.package + "`")
    if not args.apply:
        print("Nothing changed. Add --apply only after checking the package and its purpose.")
        return
    require_device()
    if input(f"Type the exact package name ({args.package}) to confirm: ").strip() != args.package:
        print("Cancelled.")
        return
    result = run_adb(["shell", "pm", "uninstall", "--user", "0", args.package], check=False)
    print(result or "ADB returned no message.")
    if "Success" in result:
        state = load_state()
        state.setdefault("removed", []).append({"name": args.package, "removed_at_utc": datetime.now(timezone.utc).isoformat()})
        save_state(state)
        print("Recorded in state/changes.json. Restore with the `restore` command.")
    else:
        raise RuntimeError("Removal was not confirmed as successful; no restore record was written.")


def cmd_restore(args: argparse.Namespace) -> None:
    validate_package(args.package)
    state = load_state()
    known = {x["name"] for x in state.get("removed", [])}
    if args.package not in known:
        raise RuntimeError("This tool has no record of removing that package. Refusing an untracked restore.")
    print("DRY RUN: would run `adb shell cmd package install-existing " + args.package + "`")
    if not args.apply:
        print("Nothing changed. Add --apply to restore it.")
        return
    require_device()
    if input(f"Type the exact package name ({args.package}) to confirm restore: ").strip() != args.package:
        print("Cancelled.")
        return
    result = run_adb(["shell", "cmd", "package", "install-existing", args.package], check=False)
    print(result or "ADB returned no message.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Careful, non-root ADB package manager for Realme phones")
    sub = p.add_subparsers(dest="command", required=True)
    for name, fn, help_text in [
        ("doctor", cmd_doctor, "Check ADB and identify the connected phone"),
        ("scan", cmd_scan, "Save a read-only package inventory"),
    ]:
        s = sub.add_parser(name, help=help_text); s.set_defaults(func=fn)
    s = sub.add_parser("list", help="List installed packages"); s.add_argument("--third-party", action="store_true"); s.set_defaults(func=cmd_list)
    s = sub.add_parser("search", help="Search package names"); s.add_argument("query"); s.set_defaults(func=cmd_search)
    s = sub.add_parser("info", help="Show basic details for one package"); s.add_argument("package"); s.set_defaults(func=cmd_info)
    s = sub.add_parser("approve", help="Manually approve a package for possible removal"); s.add_argument("package"); s.add_argument("--reason", required=True); s.set_defaults(func=cmd_approve)
    s = sub.add_parser("remove", help="Uninstall an approved package for Android user 0"); s.add_argument("package"); s.add_argument("--apply", action="store_true", help="Actually perform the change; otherwise dry-run"); s.set_defaults(func=cmd_remove)
    s = sub.add_parser("restore", help="Restore a package removed by this tool"); s.add_argument("package"); s.add_argument("--apply", action="store_true", help="Actually perform the restore; otherwise dry-run"); s.set_defaults(func=cmd_restore)
    return p


if __name__ == "__main__":
    try:
        args = build_parser().parse_args()
        args.func(args)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
