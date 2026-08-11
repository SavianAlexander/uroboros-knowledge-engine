import re
from pathlib import Path

db = Path(r'c:\Users\Administrator\Desktop\Neuro Alexander\src\infrastructure\database.py')
with open(db, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add global registry
if '_all_local_connections = set()' not in content:
    content = content.replace('_local = threading.local()', '_local = threading.local()\n_all_local_connections = set()')

# 2. Add connection to registry in get_db
# Find where it assigns _local.connection = conn
if '_all_local_connections.add(conn)' not in content:
    content = content.replace('_local.connection = conn', '_local.connection = conn\n                    _all_local_connections.add(conn)')

# 3. Modify reset_db_connections to clear all connections
old_reset = '''    # Close thread-local connection for the CURRENT thread
    if hasattr(_local, "connection") and _local.connection is not None:
        try:
            _local.connection.close()
        except Exception:
            pass
        _local.connection = None'''

new_reset = '''    # Close ALL thread-local connections
    for c in list(_all_local_connections):
        try:
            c.close()
        except Exception:
            pass
    _all_local_connections.clear()
    
    if hasattr(_local, "connection"):
        _local.connection = None'''

content = content.replace(old_reset, new_reset)

with open(db, 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched sqlite connections')
