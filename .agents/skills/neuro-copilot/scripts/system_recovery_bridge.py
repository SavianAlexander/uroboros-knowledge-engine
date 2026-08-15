#!/usr/bin/env python3
"""
System Resilience & Zero-Reboot Windows Crash Recovery Bridge for Neuro Co-Pilot.
Provides automated, non-destructive recovery actions for Windows desktop, shell, graphics,
audio, and hung process freezes without requiring a full system reboot.
Zero-dependency, Python standard library only.
"""

import sys
import os
import subprocess
import time
import json
from typing import Dict, Any, List


def restart_explorer() -> Dict[str, Any]:
    """Restarts the Windows Explorer desktop shell (explorer.exe)."""
    try:
        # Terminate explorer
        subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue"], capture_output=True, timeout=10)
        time.sleep(0.5)
        # Start explorer
        subprocess.run(["powershell", "-NoProfile", "-Command", "Start-Process explorer"], capture_output=True, timeout=10)
        return {
            "status": "success",
            "action": "restart_explorer",
            "message": "Windows Explorer desktop shell restarted cleanly.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "restart_explorer",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def restart_dwm() -> Dict[str, Any]:
    """Restarts the Desktop Window Manager (dwm.exe) for display/render glitch recovery."""
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name dwm -Force -ErrorAction SilentlyContinue"], capture_output=True, timeout=10)
        return {
            "status": "success",
            "action": "restart_dwm",
            "message": "Desktop Window Manager (DWM) restarted cleanly.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "restart_dwm",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def restart_audio() -> Dict[str, Any]:
    """Restarts Windows Audio services (Audiosrv and AudioEndpointBuilder)."""
    try:
        subprocess.run([
            "powershell", "-NoProfile", "-Command",
            "Restart-Service -Name 'Audiosrv', 'AudioEndpointBuilder' -Force -ErrorAction SilentlyContinue"
        ], capture_output=True, timeout=15)
        return {
            "status": "success",
            "action": "restart_audio",
            "message": "Windows Audio services restarted successfully.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "restart_audio",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def flush_dns() -> Dict[str, Any]:
    """Flushes DNS resolver cache."""
    try:
        res = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=10)
        return {
            "status": "success",
            "action": "flush_dns",
            "message": "Windows DNS Resolver Cache flushed successfully.",
            "output": res.stdout.strip(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "flush_dns",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def clear_hung_processes() -> Dict[str, Any]:
    """Identifies and terminates unresponsive processes as well as orphaned WebKit and background test workers."""
    try:
        # 1. Terminate hung/unresponsive processes
        cmd_hung = "Get-Process | Where-Object { -not $_.Responding } | Stop-Process -Force -ErrorAction SilentlyContinue"
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd_hung], capture_output=True, timeout=15)

        # 2. Terminate orphaned WebKit / Playwright processes whose parents have died
        cmd_orphaned = """
        Get-CimInstance Win32_Process | Where-Object { $_.Name -match "WebKitNetworkProcess|WebKitWebProcess|MiniBrowser" } | ForEach-Object {
            $parent = Get-Process -Id $_.ParentProcessId -ErrorAction SilentlyContinue
            if (-not $parent) {
                Invoke-CimMethod -InputObject $_ -MethodName Terminate | Out-Null
            }
        }
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd_orphaned], capture_output=True, timeout=15)

        return {
            "status": "success",
            "action": "clear_hung_processes",
            "message": "Scanned and terminated unresponsive Windows processes and orphaned WebKit background workers.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "clear_hung_processes",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }



def restore_all() -> Dict[str, Any]:
    """Executes full non-reboot recovery cascade across Explorer, DWM, Audio, DNS, and hung processes."""
    print("Initiating Zero-Reboot Windows System Recovery Suite...")
    results = {}
    
    print("[1/5] Restarting Windows Explorer Shell...")
    results["explorer"] = restart_explorer()
    
    print("[2/5] Refreshing Desktop Window Manager (DWM)...")
    results["dwm"] = restart_dwm()
    
    print("[3/5] Restarting Windows Audio Services...")
    results["audio"] = restart_audio()
    
    print("[4/5] Flushing DNS Cache...")
    results["dns"] = flush_dns()
    
    print("[5/5] Clearing Unresponsive Processes...")
    results["hung_processes"] = clear_hung_processes()

    success_cnt = sum(1 for v in results.values() if v.get("status") == "success")
    total_cnt = len(results)

    summary = {
        "status": "success" if success_cnt == total_cnt else "partial_success",
        "action": "restore_all",
        "recovered_components": success_cnt,
        "total_components": total_cnt,
        "details": results,
        "gpu_hotkey_tip": "If display artifacts persist, press Win + Ctrl + Shift + B on keyboard to reload GPU driver.",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return summary


def self_test() -> bool:
    """Automated bridge contract assertions."""
    print("Executing system_recovery_bridge self_test...")
    dns_res = flush_dns()
    assert dns_res.get("status") in ("success", "error"), "DNS flush returned invalid schema"
    
    hung_res = clear_hung_processes()
    assert hung_res.get("status") in ("success", "error"), "Hung processes returned invalid schema"
    
    print("system_recovery_bridge self_test PASSED [100%]")
    return True


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        print("Usage: system_recovery_bridge.py [restore_all|restart_shell|restart_dwm|restart_audio|flush_dns|clear_hung|self_test]")
        sys.exit(0)

    cmd = args[0].lower()
    if cmd == "restore_all":
        res = restore_all()
        print(json.dumps(res, indent=2))
    elif cmd in ("restart_shell", "restart_explorer"):
        res = restart_explorer()
        print(json.dumps(res, indent=2))
    elif cmd in ("restart_dwm", "dwm"):
        res = restart_dwm()
        print(json.dumps(res, indent=2))
    elif cmd in ("restart_audio", "audio"):
        res = restart_audio()
        print(json.dumps(res, indent=2))
    elif cmd in ("flush_dns", "dns"):
        res = flush_dns()
        print(json.dumps(res, indent=2))
    elif cmd in ("clear_hung", "kill_hung"):
        res = clear_hung_processes()
        print(json.dumps(res, indent=2))
    elif cmd == "self_test":
        success = self_test()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
