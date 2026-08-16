"""
Zero-Dependency Process Manager & Zombie Process Auditor.
Discovers active listeners, validates instance health, and cleanly manages background processes.
Standard-library implementation with cross-platform Windows/Linux support.
"""
import os
import sys
import time
import socket
import urllib.request
import subprocess
from typing import List, Dict, Any, Optional, Tuple


def check_uroboros_health(port: int = 8085, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Verifies whether an active Uroboros instance is responding on the specified port."""
    url = f"http://{host}:{port}/api/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UroborosProcessManager/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def is_port_bound(port: int, host: str = "127.0.0.1") -> bool:
    """Checks if a TCP port is currently bound/occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            s.bind((host, port))
            return False  # Port is available
        except OSError:
            return True   # Port is bound


def get_pid_listening_on_port(port: int) -> Optional[int]:
    """Finds the PID of the process listening on a specific TCP port using stdlib tools."""
    if sys.platform == "win32":
        try:
            output = subprocess.check_output(f'netstat -ano -p tcp | findstr ":{port} "', shell=True, text=True, errors="ignore")
            for line in output.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5 and "LISTENING" in line:
                    pid = int(parts[-1])
                    if pid != os.getpid():
                        return pid
        except Exception:
            pass
    else:
        try:
            output = subprocess.check_output(["lsof", "-t", f"-i:{port}"], text=True, errors="ignore")
            lines = output.strip().splitlines()
            if lines:
                return int(lines[0])
        except Exception:
            pass
    return None


def terminate_pid(pid: int, force: bool = True) -> Dict[str, Any]:
    """Gracefully or forcefully terminates a process by PID."""
    if pid <= 0 or pid == os.getpid():
        return {"status": "error", "message": "Cannot terminate current process or invalid PID", "pid": pid}

    try:
        if sys.platform == "win32":
            flag = "/F" if force else ""
            subprocess.run(f"taskkill /PID {pid} /T {flag}", shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            sig = 9 if force else 15
            os.kill(pid, sig)
        return {"status": "success", "message": f"Process {pid} terminated", "pid": pid}
    except Exception as e:
        return {"status": "error", "message": str(e), "pid": pid}


def list_uroboros_processes() -> Dict[str, Any]:
    """Lists current process, ports checked (8085-8095), and detected listeners."""
    current_pid = os.getpid()
    active_instances = []

    for port in range(8085, 8096):
        bound = is_port_bound(port)
        if bound:
            healthy = check_uroboros_health(port)
            listener_pid = get_pid_listening_on_port(port)
            active_instances.append({
                "port": port,
                "pid": listener_pid,
                "is_healthy": healthy,
                "is_current_process": listener_pid == current_pid,
                "status": "active_healthy" if healthy else "unresponsive_or_zombie"
            })

    return {
        "status": "success",
        "current_pid": current_pid,
        "platform": sys.platform,
        "instances": active_instances
    }


def reap_zombies_on_ports(start_port: int = 8085, end_port: int = 8095) -> Dict[str, Any]:
    """Scans Uroboros ports and forcefully reaps unresponsive zombie processes."""
    reaped = []
    current_pid = os.getpid()

    for port in range(start_port, end_port + 1):
        if is_port_bound(port):
            healthy = check_uroboros_health(port)
            if not healthy:
                pid = get_pid_listening_on_port(port)
                if pid and pid != current_pid:
                    res = terminate_pid(pid, force=True)
                    reaped.append({"port": port, "pid": pid, "result": res})

    return {
        "status": "success",
        "reaped_count": len(reaped),
        "reaped_processes": reaped
    }


class ProcessManager:
    """Zero-dependency background process and zombie lifecycle supervisor."""

    @staticmethod
    def check_health(port: int = 8085, host: str = "127.0.0.1") -> bool:
        return check_uroboros_health(port, host)

    @staticmethod
    def audit_instances(start_port: int = 8085, end_port: int = 8095):
        return audit_active_uroboros_processes(start_port, end_port)

    @staticmethod
    def reap_zombies(start_port: int = 8085, end_port: int = 8095):
        return reap_zombies_on_ports(start_port, end_port)
