import os
import re

replacements = {
    r"from main import ACTIVE_DIR as m_dir": "from src.core.config import ACTIVE_DIR as m_dir",
    r"from main import get_active_dir": "from src.core.config import ACTIVE_DIR\n        def get_active_dir(): return ACTIVE_DIR",
    r"from main import get_fallback_llm as main_get_fallback_llm": "from src.core.model_manager import get_fallback_llm as main_get_fallback_llm",
    r"from main import is_testing": "from src.core.config import is_testing",
    r"from main import ACTIVE_DIR": "from src.core.config import ACTIVE_DIR",
    r"from main import get_fallback_llm, is_testing": "from src.core.model_manager import get_fallback_llm\n        from src.core.config import is_testing",
    r"from main import is_testing, get_fallback_llm": "from src.core.config import is_testing\n        from src.core.model_manager import get_fallback_llm",
    r"import main": "# import main removed to break circular import"
}

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig = content
    for pattern, repl in replacements.items():
        content = content.replace(pattern, repl)
        
    # Also patch database.py usage of main._db_version
    content = content.replace("main._db_version", "_db_version")
    
    if orig != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")

for root, _, files in os.walk("src"):
    for file in files:
        if file.endswith(".py"):
            patch_file(os.path.join(root, file))
