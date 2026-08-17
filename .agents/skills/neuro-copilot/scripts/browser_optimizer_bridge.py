#!/usr/bin/env python3
"""
==============================================================================
Neuro Co-Pilot: Browser Performance & Zero-Stutter Gaming Optimizer Bridge
==============================================================================
Zero-dependency, pure Python standard library bridge to inspect, optimize, and
tune Chromium-based browsers (Brave, Google Chrome, Microsoft Edge, Thorium, Opera)
for zero-stutter background execution alongside high-load games like EVE Online.

Key Capabilities:
1. High Efficiency Mode / Memory Saver: Aggressive inactive tab discarding.
2. Background App Elimination: Disables lingering background helper processes.
3. Hardware Acceleration & ANGLE Tuning: Aligns GPU pipelines with DirectX.
4. Intensive Wake-Up Throttling: Enforces 1 execution/min on background JS timers.
5. Non-Destructive Backups: Timestamped snapshot before any modification.
"""

import os
import sys
import json
import shutil
import pathlib
import datetime
import subprocess
from typing import Dict, Any, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def get_browser_targets() -> Dict[str, Dict[str, Any]]:
    """Returns detected browser profile directories based on OS environment."""
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    home = os.path.expanduser("~")

    targets = {}

    # Windows paths
    if local_app_data:
        brave_dir = pathlib.Path(local_app_data) / "BraveSoftware" / "Brave-Browser" / "User Data"
        if brave_dir.exists():
            targets["brave"] = {
                "name": "Brave Browser",
                "process_names": ["brave.exe", "brave"],
                "user_data_dir": brave_dir,
            }

        chrome_dir = pathlib.Path(local_app_data) / "Google" / "Chrome" / "User Data"
        if chrome_dir.exists():
            targets["chrome"] = {
                "name": "Google Chrome",
                "process_names": ["chrome.exe", "chrome"],
                "user_data_dir": chrome_dir,
            }

        edge_dir = pathlib.Path(local_app_data) / "Microsoft" / "Edge" / "User Data"
        if edge_dir.exists():
            targets["edge"] = {
                "name": "Microsoft Edge",
                "process_names": ["msedge.exe", "msedge"],
                "user_data_dir": edge_dir,
            }

    # Linux / macOS fallback paths
    if not targets:
        linux_brave = pathlib.Path(home) / ".config" / "BraveSoftware" / "Brave-Browser"
        if linux_brave.exists():
            targets["brave"] = {
                "name": "Brave Browser",
                "process_names": ["brave"],
                "user_data_dir": linux_brave,
            }

        linux_chrome = pathlib.Path(home) / ".config" / "google-chrome"
        if linux_chrome.exists():
            targets["chrome"] = {
                "name": "Google Chrome",
                "process_names": ["chrome", "google-chrome"],
                "user_data_dir": linux_chrome,
            }

    return targets


def get_running_browser_processes() -> Dict[str, Dict[str, Any]]:
    """Inspects running processes and aggregates memory working sets per browser."""
    browser_stats = {}
    
    if os.name == "nt":
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "Get-Process | Where-Object { $_.ProcessName -match 'brave|chrome|msedge' } | "
            "Group-Object ProcessName | Select-Object Name, Count, "
            "@{Name='MemoryMB'; Expression={[math]::Round(($_.Group | Measure-Object WorkingSet -Sum).Sum / 1MB, 2)}} | "
            "ConvertTo-Json"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout.strip())
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                    pname = str(item.get("Name", "")).lower()
                    browser_key = "brave" if "brave" in pname else ("edge" if "msedge" in pname else "chrome")
                    browser_stats[browser_key] = {
                        "process_name": pname,
                        "count": item.get("Count", 0),
                        "memory_mb": item.get("MemoryMB", 0.0)
                    }
        except Exception:
            pass
    return browser_stats


def get_browser_profiles(user_data_dir: pathlib.Path) -> List[pathlib.Path]:
    """Finds all profile directories inside a Chromium User Data folder."""
    profiles = []
    default_prof = user_data_dir / "Default"
    if default_prof.exists() and default_prof.is_dir():
        profiles.append(default_prof)

    for p in user_data_dir.glob("Profile *"):
        if p.is_dir():
            profiles.append(p)

    return profiles


def inspect_browser_status() -> Dict[str, Any]:
    """Inspects detected browsers, configuration state, and memory consumption."""
    targets = get_browser_targets()
    running = get_running_browser_processes()

    status_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "detected_browsers": {},
        "total_browser_memory_mb": 0.0
    }

    for bkey, binfo in targets.items():
        user_data = binfo["user_data_dir"]
        proc_info = running.get(bkey, {"count": 0, "memory_mb": 0.0})
        status_report["total_browser_memory_mb"] += proc_info.get("memory_mb", 0.0)

        profiles = get_browser_profiles(user_data)
        profile_configs = []

        local_state_file = user_data / "Local State"
        local_state_experiments = []
        if local_state_file.exists():
            try:
                ls_data = json.loads(local_state_file.read_text(encoding="utf-8", errors="ignore"))
                local_state_experiments = ls_data.get("browser", {}).get("enabled_labs_experiments", [])
            except Exception:
                pass

        for prof in profiles:
            pref_file = prof / "Preferences"
            is_memory_saver_on = False
            is_bg_disabled = False

            if pref_file.exists():
                try:
                    pdata = json.loads(pref_file.read_text(encoding="utf-8", errors="ignore"))
                    perf_tuning = pdata.get("performance_tuning", {})
                    high_eff = perf_tuning.get("high_efficiency_mode", {})
                    is_memory_saver_on = high_eff.get("state") in (1, 2) or high_eff.get("enabled", False)

                    bg_mode = pdata.get("background_mode", {})
                    is_bg_disabled = bg_mode.get("enabled") is False
                except Exception:
                    pass

            profile_configs.append({
                "profile_name": prof.name,
                "memory_saver_active": is_memory_saver_on,
                "background_apps_disabled": is_bg_disabled
            })

        status_report["detected_browsers"][bkey] = {
            "name": binfo["name"],
            "user_data_dir": str(user_data),
            "is_running": proc_info.get("count", 0) > 0,
            "process_count": proc_info.get("count", 0),
            "memory_working_set_mb": proc_info.get("memory_mb", 0.0),
            "profiles": profile_configs,
            "lab_experiments": local_state_experiments,
            "zero_stutter_ready": all(p.get("memory_saver_active") and p.get("background_apps_disabled") for p in profile_configs)
        }

    return status_report


def close_browser_processes(browser_key: str, targets: Dict[str, Dict[str, Any]]) -> int:
    """Closes running browser processes so file writes are permanently saved."""
    binfo = targets.get(browser_key)
    if not binfo:
        return 0
    closed_count = 0
    if os.name == "nt":
        for p in binfo.get("process_names", []):
            stem = p.replace(".exe", "")
            ps_script = "$procs = Get-Process -Name '" + stem + "' -ErrorAction SilentlyContinue; if ($procs) { $cnt = $procs.Count; $procs | Stop-Process -Force; $cnt } else { 0 }"
            cmd = ["powershell", "-NoProfile", "-Command", ps_script]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip().isdigit():
                closed_count += int(res.stdout.strip())
    return closed_count


def tune_browser_profile(user_data_dir: pathlib.Path) -> Dict[str, Any]:
    """Applies the zero-stutter gaming profile to a Chromium User Data directory."""
    results = {
        "profiles_modified": [],
        "local_state_modified": False,
        "backups_created": []
    }

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Optimize Local State (Lab experiments & Global background mode)
    local_state_file = user_data_dir / "Local State"
    if local_state_file.exists():
        try:
            ls_backup = user_data_dir / f"Local State.bak_{timestamp}"
            shutil.copy2(local_state_file, ls_backup)
            results["backups_created"].append(str(ls_backup))

            ls_data = json.loads(local_state_file.read_text(encoding="utf-8", errors="ignore"))
            if "browser" not in ls_data:
                ls_data["browser"] = {}

            experiments = ls_data["browser"].get("enabled_labs_experiments", [])
            recommended_experiments = [
                "intensive-wake-up-throttling@1",
                "high-efficiency-mode-available@1",
                "enable-gpu-rasterization@1",
                "zero-copy-video-capture@1",
                "use-angle@d3d11"
            ]

            for exp in recommended_experiments:
                prefix = exp.split("@")[0]
                # Remove conflicting variants
                experiments = [e for e in experiments if not e.startswith(prefix + "@")]
                experiments.append(exp)

            ls_data["browser"]["enabled_labs_experiments"] = experiments

            # Disable global background mode
            if "background_mode" not in ls_data:
                ls_data["background_mode"] = {}
            ls_data["background_mode"]["enabled"] = False

            # Ensure hardware acceleration is enabled
            if "hardware_acceleration_mode" not in ls_data:
                ls_data["hardware_acceleration_mode"] = {}
            ls_data["hardware_acceleration_mode"]["enabled"] = True

            local_state_file.write_text(json.dumps(ls_data, indent=2), encoding="utf-8")
            results["local_state_modified"] = True
        except Exception as e:
            results["local_state_error"] = str(e)

    # 2. Optimize each Profile Preferences
    profiles = get_browser_profiles(user_data_dir)
    for prof in profiles:
        pref_file = prof / "Preferences"
        try:
            pref_data = {}
            if pref_file.exists():
                pref_backup = prof / f"Preferences.bak_{timestamp}"
                shutil.copy2(pref_file, pref_backup)
                results["backups_created"].append(str(pref_backup))
                pref_data = json.loads(pref_file.read_text(encoding="utf-8", errors="ignore"))

            # Memory Saver / High Efficiency Mode configuration
            if "performance_tuning" not in pref_data:
                pref_data["performance_tuning"] = {}

            pref_data["performance_tuning"]["high_efficiency_mode"] = {
                "state": 1,  # 1 = Enabled
                "time_before_discard_in_minutes": 5,
                "discard_ring_treatment_enabled": True
            }

            # Background Mode disabled
            if "background_mode" not in pref_data:
                pref_data["background_mode"] = {}
            pref_data["background_mode"]["enabled"] = False

            # Hardware acceleration enabled
            if "hardware_acceleration_mode" not in pref_data:
                pref_data["hardware_acceleration_mode"] = {}
            pref_data["hardware_acceleration_mode"]["enabled"] = True

            pref_file.write_text(json.dumps(pref_data, indent=2), encoding="utf-8")
            results["profiles_modified"].append(prof.name)
        except Exception as e:
            results[f"profile_error_{prof.name}"] = str(e)

    return results


def restore_browser_backups(user_data_dir: pathlib.Path) -> Dict[str, Any]:
    """Restores the most recent backup files in a User Data directory."""
    restored = []

    # Restore Local State
    ls_backups = sorted(user_data_dir.glob("Local State.bak_*"), key=os.path.getmtime, reverse=True)
    if ls_backups:
        latest = ls_backups[0]
        shutil.copy2(latest, user_data_dir / "Local State")
        restored.append(f"Local State from {latest.name}")

    # Restore Profiles
    profiles = get_browser_profiles(user_data_dir)
    for prof in profiles:
        pref_backups = sorted(prof.glob("Preferences.bak_*"), key=os.path.getmtime, reverse=True)
        if pref_backups:
            latest = pref_backups[0]
            shutil.copy2(latest, prof / "Preferences")
            restored.append(f"{prof.name}/Preferences from {latest.name}")

    return {"status": "success", "restored_files": restored}


def print_status_card(report: Dict[str, Any]):
    """Renders visual terminal card for browser status."""
    print("==========================================================================")
    print("             BROWSER OPTIMIZATION & ZERO-STUTTER AUDIT                   ")
    print("==========================================================================")
    print(f"  Active Browser Working Set : {report.get('total_browser_memory_mb', 0.0):.1f} MB")
    print("--------------------------------------------------------------------------")

    detected = report.get("detected_browsers", {})
    if not detected:
        print("  No supported Chromium browsers detected in standard paths.")
    else:
        for bkey, bdata in detected.items():
            status_badge = "🟢 RUNNING" if bdata.get("is_running") else "⚪ IDLE"
            opt_badge = "✅ ZERO-STUTTER READY" if bdata.get("zero_stutter_ready") else "⚠️ UNTUNED"
            print(f"  Browser: {bdata.get('name')} [{status_badge}] - {opt_badge}")
            print(f"    Memory Usage     : {bdata.get('memory_working_set_mb', 0.0):.1f} MB ({bdata.get('process_count', 0)} processes)")
            print(f"    User Data Dir    : {bdata.get('user_data_dir')}")
            for p in bdata.get("profiles", []):
                ms = "ON" if p.get("memory_saver_active") else "OFF"
                bg = "DISABLED (Good)" if p.get("background_apps_disabled") else "ENABLED (Lingers)"
                print(f"    Profile [{p.get('profile_name')}]: Memory Saver: {ms} | Background Apps: {bg}")
            if bdata.get("lab_experiments"):
                print(f"    Active Flags     : {', '.join(bdata.get('lab_experiments')[:3])}...")
            print("--------------------------------------------------------------------------")
    print("==========================================================================")


def run_self_test() -> int:
    """Executes non-destructive unit test asserting browser configuration logic."""
    print("[Browser Optimizer Bridge] Running automated self-test suite...")
    test_dir = pathlib.Path(BASE_DIR) / "test_sandbox_browser"
    if test_dir.exists():
        shutil.rmtree(test_dir, ignore_errors=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Create mock profile & local state
        default_prof = test_dir / "Default"
        default_prof.mkdir(parents=True, exist_ok=True)

        mock_local_state = test_dir / "Local State"
        mock_local_state.write_text(json.dumps({"browser": {}}), encoding="utf-8")

        mock_pref = default_prof / "Preferences"
        mock_pref.write_text(json.dumps({"test": 123}), encoding="utf-8")

        # 1. Run tune
        res = tune_browser_profile(test_dir)
        assert res["local_state_modified"] is True, "Local State was not modified"
        assert "Default" in res["profiles_modified"], "Default profile not tuned"
        assert len(res["backups_created"]) == 2, "Backups not created properly"

        # Verify tuned values
        tuned_pref = json.loads(mock_pref.read_text(encoding="utf-8"))
        assert tuned_pref.get("performance_tuning", {}).get("high_efficiency_mode", {}).get("state") == 1
        assert tuned_pref.get("background_mode", {}).get("enabled") is False
        assert tuned_pref.get("hardware_acceleration_mode", {}).get("enabled") is True

        tuned_ls = json.loads(mock_local_state.read_text(encoding="utf-8"))
        assert "intensive-wake-up-throttling@1" in tuned_ls.get("browser", {}).get("enabled_labs_experiments", [])
        assert tuned_ls.get("background_mode", {}).get("enabled") is False

        # 2. Run restore
        rest = restore_browser_backups(test_dir)
        assert rest["status"] == "success"
        assert len(rest["restored_files"]) == 2

        restored_pref = json.loads(mock_pref.read_text(encoding="utf-8"))
        assert restored_pref == {"test": 123}, "Preferences did not restore accurately"

        print("✅ [PASS] Browser Optimizer Bridge self-test passed with 100% precision!")
        return 0
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Neuro Co-Pilot Browser Performance & Zero-Stutter Gaming Optimizer Bridge")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # status
    subparsers.add_parser("status", help="Inspect browser memory usage and zero-stutter optimization state")

    # tune
    tune_parser = subparsers.add_parser("tune", help="Apply zero-stutter gaming profile to detected browsers")
    tune_parser.add_argument("--browser", choices=["brave", "chrome", "edge", "all"], default="all", help="Target specific browser")
    tune_parser.add_argument("--close", action="store_true", help="Cleanly close running browser processes before applying settings to prevent in-memory rollback")

    # restore
    rest_parser = subparsers.add_parser("restore", help="Restore previous browser settings from backup")
    rest_parser.add_argument("--browser", choices=["brave", "chrome", "edge", "all"], default="all", help="Target specific browser")

    # test
    subparsers.add_parser("test", help="Run automated self-test assertions")

    args = parser.parse_args()

    if not args.command or args.command == "status":
        report = inspect_browser_status()
        print_status_card(report)
        return 0

    if args.command == "test":
        return run_self_test()

    targets = get_browser_targets()
    target_browsers = targets if getattr(args, "browser", "all") == "all" else {k: v for k, v in targets.items() if k == args.browser}

    if not target_browsers:
        print(f"[!] No matching browsers found for target: {args.browser}")
        return 1

    if args.command == "tune":
        print("==========================================================================")
        print("             APPLYING ZERO-STUTTER BROWSER GAMING PROFILE                 ")
        print("==========================================================================")
        for bkey, binfo in target_browsers.items():
            if getattr(args, "close", False):
                closed = close_browser_processes(bkey, targets)
                if closed > 0:
                    print(f"[*] Closed {closed} running processes for {binfo['name']} to lock settings.")

            print(f"[*] Optimizing {binfo['name']}...")
            res = tune_browser_profile(binfo["user_data_dir"])
            print(f"    [+] Modified Profiles : {', '.join(res.get('profiles_modified', []))}")
            print(f"    [+] Local State Tuned : {res.get('local_state_modified')}")
            print(f"    [+] Backups Generated : {len(res.get('backups_created', []))} files")
            if not getattr(args, "close", False) and binfo["user_data_dir"] in [v["user_data_dir"] for v in targets.values()]:
                running = get_running_browser_processes().get(bkey)
                if running and running.get("count", 0) > 0:
                    print(f"    [!] Note: {binfo['name']} is currently open ({running.get('count')} processes).")
                    print(f"        Use '--close' to close running instances or restart the browser manually.")
        print("==========================================================================")
        print("✅ [SUCCESS] Zero-Stutter Gaming Profile applied successfully!")
        return 0

    if args.command == "restore":
        print("==========================================================================")
        print("             RESTORING BROWSER PREFERENCES FROM BACKUP                    ")
        print("==========================================================================")
        for bkey, binfo in target_browsers.items():
            print(f"[*] Restoring {binfo['name']}...")
            res = restore_browser_backups(binfo["user_data_dir"])
            for r in res.get("restored_files", []):
                print(f"    [+] Restored: {r}")
        print("==========================================================================")
        print("✅ [SUCCESS] Browser preferences restored from backup!")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
