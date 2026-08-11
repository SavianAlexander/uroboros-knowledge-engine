import ast
import os

db_path = r"c:\Users\Administrator\Desktop\Neuro Alexander\src\infrastructure\database.py"

with open(db_path, "r", encoding="utf-8") as f:
    source = f.read()

lines = source.split("\n")

def get_source(node):
    start = node.lineno - 1
    end = node.end_lineno
    # Include any decorators
    if hasattr(node, "decorator_list") and node.decorator_list:
        start = node.decorator_list[0].lineno - 1
    return "\n".join(lines[start:end])

tree = ast.parse(source)

modules = {
    "files": [],
    "snapshots": [],
    "chat": [],
    "workflows": [],
    "vector_engine": [],
    "database_core": []
}

core_funcs = ["get_pool", "reset_db_connections", "get_db_write_connection", "get_db_connection", "get_active_dir", "get_db", "backup_db_online", "init_db", "migrate_folder_path", "run_maintenance", "db_status"]
vector_funcs = ["search_files", "index_directory", "extract_rag_context"]

imports = []
for node in tree.body:
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        imports.append(get_source(node))
    elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
        name = node.name
        if name in core_funcs:
            modules["database_core"].append(get_source(node))
        elif name in vector_funcs or name.startswith("_"):
            # Some internal helpers might belong in vector_engine
            if name.startswith("extract") or name.startswith("search") or name.startswith("index"):
                modules["vector_engine"].append(get_source(node))
            else:
                modules["database_core"].append(get_source(node))
        elif "chat" in name:
            modules["chat"].append(get_source(node))
        elif "workflow" in name:
            modules["workflows"].append(get_source(node))
        elif "snapshot" in name:
            modules["snapshots"].append(get_source(node))
        elif "file" in name:
            modules["files"].append(get_source(node))
        else:
            modules["database_core"].append(get_source(node))
    elif isinstance(node, ast.ClassDef):
        name = node.name
        if name == "SQLiteConnectionPool":
            modules["database_core"].append(get_source(node))
        elif name == "MiniVectorEngine":
            modules["vector_engine"].append(get_source(node))
        else:
            modules["database_core"].append(get_source(node))
    else:
        # Top level constants/globals
        modules["database_core"].append(get_source(node))

import_block = "\n".join(imports)

for mod_name, code_blocks in modules.items():
    if mod_name == "database_core":
        continue
    content = import_block + "\n\n" + "\n\n".join(code_blocks)
    if mod_name == "vector_engine":
        path = r"c:\Users\Administrator\Desktop\Neuro Alexander\src\infrastructure\vector_engine.py"
    else:
        path = rf"c:\Users\Administrator\Desktop\Neuro Alexander\src\infrastructure\repositories\{mod_name}.py"
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Update database.py to just be core
core_content = import_block + "\n\n" + "\n\n".join(modules["database_core"])
with open(db_path, "w", encoding="utf-8") as f:
    f.write(core_content)

print("Split complete!")
