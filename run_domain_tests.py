import os
import sys
import time
import subprocess
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.update_test_ledger import run_ledger_audit, FILE_DOMAIN_MAPPING, DOMAIN_TEST_MODULES

def get_modified_git_files():
    try:
        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        modified_files = []
        for line in lines:
            if line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    modified_files.append(os.path.basename(parts[-1]))
        return modified_files
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in run_domain_tests.py")
        return []

def main_runner():
    print("===================================================")
    print("   UROBOROS DOMAIN TEST RUNNER v2.0")
    print("===================================================")
    
    is_fast_mode = "--fast" in sys.argv or "--changed-only" in sys.argv
    target_modules = None

    if is_fast_mode:
        modified_files = get_modified_git_files()
        print(f"[FAST MODE] Modified git files detected: {modified_files}")
        if modified_files:
            matched_domains = set()
            for fname in modified_files:
                domains = FILE_DOMAIN_MAPPING.get(fname, [])
                for d in domains:
                    matched_domains.add(f"tests.test_{d.lower()}")
            
            target_modules = [m for m in DOMAIN_TEST_MODULES if m in matched_domains]
            if not target_modules:
                print("[FAST MODE] No direct domain mapping found. Running all modules.")
                target_modules = DOMAIN_TEST_MODULES
        else:
            print("[FAST MODE] No modified files detected. Running full audit.")
            target_modules = DOMAIN_TEST_MODULES

    t0 = time.time()
    run_ledger_audit(target_modules=target_modules)
    t1 = time.time()
    print("===================================================")
    print(f"  ALL DOMAIN TESTS COMPLETE - Total Time: {t1-t0:.2f}s")
    print("===================================================")

if __name__ == "__main__":
    main_runner()
