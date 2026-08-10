import os
import json
import time
import socket
import struct
import threading
import hashlib
import urllib.request
from typing import List, Dict, Any, Optional

MULTICAST_GROUP = "239.255.255.250"
UDP_PORT = 8098
BROADCAST_INTERVAL = 3.0
DISCOVERED_PEERS: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()

class P2PPeerBeacon:
    def __init__(self, node_id: str, http_port: int):
        self.node_id = node_id
        self.http_port = http_port
        self.running = False
        self._thread = None
        self._listener_thread = None

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._thread.start()

        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener_thread.start()

    def stop(self):
        self.running = False

    def _broadcast_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")
        sock.settimeout(1.0)
        
        message = json.dumps({"node_id": self.node_id, "port": self.http_port, "ts": time.time()}).encode("utf-8")
        while self.running:
            try:
                sock.sendto(message, (MULTICAST_GROUP, UDP_PORT))
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")
            for _ in range(int(BROADCAST_INTERVAL * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
        sock.close()

    def _listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")

        bound = False
        for bind_addr in ["", "0.0.0.0"]:
            try:
                sock.bind((bind_addr, UDP_PORT))
                bound = True
                break
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception:
                import logging; logging.getLogger(__name__).exception("Swallowed error in p2p_sync.py")
                continue

        if not bound:
            sock.close()
            return

        try:
            mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")

        sock.settimeout(1.0)

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                info = json.loads(data.decode("utf-8"))
                peer_ip = addr[0]
                peer_node_id = info.get("node_id")
                peer_port = info.get("port")

                if peer_node_id and peer_node_id != self.node_id:
                    with _lock:
                        DISCOVERED_PEERS[peer_node_id] = {
                            "node_id": peer_node_id,
                            "ip": peer_ip,
                            "port": peer_port,
                            "last_seen": time.time()
                        }
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception as e:
                import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")
        sock.close()

def get_active_peers() -> List[Dict[str, Any]]:
    """Return a list of auto-discovered LAN sync nodes seen within the last 15 seconds."""
    now = time.time()
    with _lock:
        active = []
        for peer in list(DISCOVERED_PEERS.values()):
            if now - peer["last_seen"] < 15.0:
                active.append(peer)
        return active

def get_local_document_hashes(vault_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Generate SHA-256 hashes, sizes, and timestamps for all local indexed documents."""
    hashes = {}
    try:
        from src.infrastructure.database import get_db, get_active_dir
        target_dir = vault_dir or get_active_dir()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath, filename, file_size, modified_at, content FROM files")
            rows = cursor.fetchall()
            for r in rows:
                fp = r["filepath"] if hasattr(r, "keys") else r[0]
                fn = r["filename"] if hasattr(r, "keys") else (r[1] or os.path.basename(fp or ""))
                if not fn and fp:
                    fn = os.path.basename(fp)
                if not fn:
                    continue

                content = r["content"] if hasattr(r, "keys") else (r[4] or "")
                size = (r["file_size"] if hasattr(r, "keys") else r[3]) or 0
                mod_at = (r["modified_at"] if hasattr(r, "keys") else r[2]) or 0.0

                sha256_val = ""
                if fp and os.path.exists(fp) and os.path.isfile(fp):
                    try:
                        with open(fp, "rb") as f:
                            sha256_val = hashlib.sha256(f.read()).hexdigest()
                        size = os.path.getsize(fp)
                        mod_at = os.path.getmtime(fp)
                    except (KeyboardInterrupt, MemoryError, SystemExit):
                        raise
                    except Exception as e:
                        import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")

                if not sha256_val and content:
                    sha256_val = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    if not size:
                        size = len(content.encode("utf-8"))

                try:
                    mod_at_float = float(mod_at)
                except (ValueError, TypeError):
                    mod_at_float = time.time()

                hashes[fn] = {
                    "filepath": fp or "",
                    "filename": fn,
                    "sha256": sha256_val,
                    "size": size,
                    "modified_at": mod_at_float
                }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")

    try:
        from src.infrastructure.database import get_active_dir
        target_dir = vault_dir or get_active_dir()
        if target_dir and os.path.exists(target_dir) and os.path.isdir(target_dir):
            EXCLUDE_DIRS = {".git", "__pycache__", ".agents", "dist", "build", ".venv", "node_modules", ".pytest_cache"}
            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
                for fname in files:
                    if fname not in hashes:
                        full_p = os.path.join(root, fname)
                        try:
                            with open(full_p, "rb") as f:
                                sha256_val = hashlib.sha256(f.read()).hexdigest()
                            sz = os.path.getsize(full_p)
                            mt = os.path.getmtime(full_p)
                            hashes[fname] = {
                                "filepath": full_p,
                                "filename": fname,
                                "sha256": sha256_val,
                                "size": sz,
                                "modified_at": mt
                            }
                        except (KeyboardInterrupt, MemoryError, SystemExit):
                            raise
                        except Exception as e:
                            import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.error(f"Swallowed error in p2p_sync.py: {e}")

    return hashes

def compute_sync_delta(local_hashes: Dict[str, Dict[str, Any]], remote_hashes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare local SHA-256 document hashes against remote hashes.
    Return categorized lists of files: missing, outdated, unchanged, and to_pull.
    """
    missing = []
    outdated = []
    unchanged = []

    for fn, r_info in remote_hashes.items():
        r_hash = r_info.get("sha256", "") if isinstance(r_info, dict) else ""
        r_mtime = float(r_info.get("modified_at", 0.0)) if isinstance(r_info, dict) else 0.0

        if fn not in local_hashes:
            missing.append(fn)
        else:
            l_info = local_hashes[fn]
            l_hash = l_info.get("sha256", "") if isinstance(l_info, dict) else ""
            l_mtime = float(l_info.get("modified_at", 0.0)) if isinstance(l_info, dict) else 0.0

            if r_hash and r_hash == l_hash:
                unchanged.append(fn)
            else:
                if r_mtime >= l_mtime or not l_hash:
                    outdated.append(fn)
                else:
                    unchanged.append(fn)

    to_pull = missing + outdated
    return {
        "missing": missing,
        "outdated": outdated,
        "unchanged": unchanged,
        "to_pull": to_pull
    }

