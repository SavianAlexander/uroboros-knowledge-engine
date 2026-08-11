import os
import re
from pathlib import Path

# Mapping of function names to their new modules
MAPPING = {
    "MiniVectorEngine": "src.infrastructure.vector_engine",
    "search_files": "src.infrastructure.vector_engine",
    "index_directory": "src.infrastructure.vector_engine",
    "extract_rag_context": "src.infrastructure.vector_engine",

    "save_file_revision": "src.infrastructure.repositories.files",
    "get_file_revisions": "src.infrastructure.repositories.files",
    "revert_file_revision": "src.infrastructure.repositories.files",

    "create_db_snapshot": "src.infrastructure.repositories.snapshots",
    "restore_db_snapshot": "src.infrastructure.repositories.snapshots",
    "delete_db_snapshot": "src.infrastructure.repositories.snapshots",
    "list_db_snapshots": "src.infrastructure.repositories.snapshots",

    "create_chat_session": "src.infrastructure.repositories.chat",
    "list_chat_sessions": "src.infrastructure.repositories.chat",
    "get_chat_session": "src.infrastructure.repositories.chat",
    "update_chat_session": "src.infrastructure.repositories.chat",
    "delete_chat_session": "src.infrastructure.repositories.chat",
    "add_chat_message": "src.infrastructure.repositories.chat",
    "get_chat_messages": "src.infrastructure.repositories.chat",

    "create_workflow_trigger": "src.infrastructure.repositories.workflows",
    "list_workflow_triggers": "src.infrastructure.repositories.workflows",
    "get_workflow_trigger": "src.infrastructure.repositories.workflows",
    "update_workflow_trigger": "src.infrastructure.repositories.workflows",
    "delete_workflow_trigger": "src.infrastructure.repositories.workflows",
    "log_workflow_execution": "src.infrastructure.repositories.workflows",
    "list_workflow_logs": "src.infrastructure.repositories.workflows",
}

# The files we need to check
root_dir = Path(r"c:\Users\Administrator\Desktop\Neuro Alexander")
targets = list(root_dir.glob("src/**/*.py")) + list(root_dir.glob("tests/**/*.py")) + [root_dir / "know.py", root_dir / "main.py"]

import_pattern = re.compile(r"from src\.infrastructure\.database import \((.*?)\)", re.DOTALL)
import_inline_pattern = re.compile(r"from src\.infrastructure\.database import (.*)")

def rewrite_imports(content):
    # First, handle multiline imports
    def replace_multiline(match):
        names = [n.strip() for n in match.group(1).replace("\n", "").split(",") if n.strip()]
        new_imports = {}
        for name in names:
            mod = MAPPING.get(name, "src.infrastructure.database")
            if mod not in new_imports:
                new_imports[mod] = []
            new_imports[mod].append(name)
        
        replacement = ""
        for mod, nms in new_imports.items():
            replacement += f"from {mod} import {', '.join(nms)}\n"
        return replacement.strip()

    content = import_pattern.sub(replace_multiline, content)

    # Now handle single-line imports
    def replace_singleline(match):
        names = [n.strip() for n in match.group(1).split(",") if n.strip()]
        new_imports = {}
        for name in names:
            mod = MAPPING.get(name, "src.infrastructure.database")
            if mod not in new_imports:
                new_imports[mod] = []
            new_imports[mod].append(name)
        
        replacement = ""
        for mod, nms in new_imports.items():
            replacement += f"from {mod} import {', '.join(nms)}\n"
        return replacement.strip()

    content = import_inline_pattern.sub(replace_singleline, content)
    return content

for target in targets:
    if not target.exists() or target.name == "database.py" or "infrastructure\\repositories" in str(target) or "vector_engine.py" in str(target):
        continue
    
    with open(target, "r", encoding="utf-8") as f:
        original = f.read()
    
    new_content = rewrite_imports(original)
    
    if original != new_content:
        with open(target, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated imports in {target.name}")

# Finally, remove the re-exports from database.py to fix the circular import
db_file = root_dir / "src" / "infrastructure" / "database.py"
with open(db_file, "r", encoding="utf-8") as f:
    db_content = f.read()

# Strip out everything after the re-exports were added
# We know we appended them with \nfrom src.infrastructure.vector_engine import *
if "\nfrom src.infrastructure.vector_engine import *" in db_content:
    db_content = db_content.split("\nfrom src.infrastructure.vector_engine import *")[0]
    with open(db_file, "w", encoding="utf-8") as f:
        f.write(db_content)
    print("Stripped facade re-exports from database.py")
