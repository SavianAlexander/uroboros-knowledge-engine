import sqlite3
import os
import glob

def check():
    candidates = glob.glob("*.db") + glob.glob("data/*.db") + glob.glob("data/**/*.db", recursive=True) + glob.glob("vault/*.db")
    for db in candidates:
        if "snapshots" in db:
            continue
        if not os.path.exists(db):
            continue
        try:
            conn = sqlite3.connect(db)
            c = conn.cursor()
            tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            print(f"=== DB: {db} ===")
            print(f"Tables: {tables}")
            if "files" in tables:
                total = c.execute("SELECT COUNT(*) FROM files").fetchone()[0]
                rows = c.execute("SELECT id, filepath FROM files").fetchall()
                missing = []
                for fid, fpath in rows:
                    if not os.path.exists(fpath):
                        missing.append((fid, fpath))
                print(f"Files count: {total}, Missing on disk: {len(missing)}")
                if missing:
                    print(f"Sample missing: {missing[:5]}")
            conn.close()
        except Exception as ex:
            print(f"Error checking {db}: {ex}")

if __name__ == "__main__":
    check()
