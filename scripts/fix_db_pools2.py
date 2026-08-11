import os
from pathlib import Path

db = Path(r'c:\Users\Administrator\Desktop\Neuro Alexander\src\infrastructure\database.py')
with open(db, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix indentation and remove _all_local_connections
content = content.replace('_local = threading.local()\n_all_local_connections = set()', '_local = threading.local()')

content = content.replace('_local.connection = conn\n                    _all_local_connections.add(conn)', '_local.connection = conn')

old_reset = '''    # Close ALL thread-local connections
    for c in list(_all_local_connections):
        try:
            c.close()
        except Exception:
            pass
    _all_local_connections.clear()
    
    if hasattr(_local, "connection"):
        _local.connection = None'''

new_reset = '''    # Close ALL thread-local connections
    with _local_connections_lock:
        for c in _local_connections:
            try:
                c.close()
            except Exception:
                pass
        _local_connections.clear()
    
    if hasattr(_local, "connection"):
        _local.connection = None'''

content = content.replace(old_reset, new_reset)

with open(db, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed database.py syntax error and updated reset logic')
