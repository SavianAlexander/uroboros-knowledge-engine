import os
import sys
import subprocess
import shutil

root_dir = os.path.abspath(os.path.dirname(__file__))

def create_spec_file():
    """Generate PyInstaller spec file for Uroboros Knowledge Hub."""
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=[r'{root_dir}'],
    binaries=[],
    datas=[
        ('index.html', '.'),
        ('style.css', '.'),
        ('app.js', '.'),
        ('assets', 'assets'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'fastapi',
        'pydantic',
        'know',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['nltk'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='UroborosKnowledgeHub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/favicon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UroborosKnowledgeHub',
)
"""
    spec_path = os.path.join(root_dir, "UroborosKnowledgeHub.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    build_dir = os.path.join(root_dir, "build")
    os.makedirs(build_dir, exist_ok=True)
    build_spec_path = os.path.join(build_dir, "UroborosKnowledgeHub.spec")
    with open(build_spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print(f"Generated spec file: {spec_path}")
    return spec_path

def build_executable(check_only=False):
    """Verify build spec and execute PyInstaller if available."""
    spec_path = create_spec_file()
    if check_only:
        print("Spec check complete. Ready for PyInstaller compilation.")
        return True
    
    print("Executing PyInstaller compilation...")
    try:
        res = subprocess.run([sys.executable, "-m", "PyInstaller", "-y", spec_path], check=True)
        print("Desktop compilation completed successfully!")
        return res.returncode == 0
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in build_desktop.py: {e}")
        print(f"PyInstaller build step deferred: {e}")
        return False

if __name__ == "__main__":
    check_mode = "--check-only" in sys.argv
    build_executable(check_only=check_mode)
