import os
import re

def patch_sqlite_connect(directories):
    count = 0
    for d in directories:
        for root, dirs, files in os.walk(d):
            if any(ignore in root for ignore in ['node_modules', '.git', 'frontend', '.venv']):
                continue
                
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                orig = content
                
                # Replace get_db_connection(...)
                content = re.sub(r'contextlib\.closing\(\s*sqlite3\.connect\(([^)]+)\)\s*\)', r'get_db_connection(\1)', content)
                
                # Replace raw sqlite3.connect in 'with' statements that weren't wrapped
                # Note: only replacing if it's not already get_db_connection
                # Actually, some places do `conn = sqlite3.connect(...)` which is harder to patch.
                # Let's just fix the 'with sqlite3.connect' ones
                content = re.sub(r'with sqlite3\.connect\(([^)]+)\)', r'with get_db_connection(\1)', content)
                
                if orig != content:
                    # We need to make sure get_db_connection is imported
                    if "get_db_connection" not in content and "def get_db_connection" not in content:
                        import_stmt = "from src.infrastructure.database import get_db_connection"
                        # Insert after imports
                        content = import_stmt + "\n" + content
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1
                    print(f"Patched {filepath}")

    print(f"Patched {count} files for sqlite3 connections.")

if __name__ == '__main__':
    patch_sqlite_connect(['src', 'tests', 'scripts'])
