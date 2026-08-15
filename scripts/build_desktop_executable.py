"""
PyInstaller Standalone Desktop Executable Build Script.
Generates UroborosKnowledgeHub.spec and builds single-file Windows desktop application.
"""
import os
import sys
import subprocess
import shutil

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def create_spec_file():
    """Generate PyInstaller spec file for Uroboros Knowledge Hub."""
    os.makedirs(os.path.join(root_dir, "build"), exist_ok=True)
    os.makedirs(os.path.join(root_dir, "dist"), exist_ok=True)

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
        ('src/assets', 'src/assets'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'pydantic',
        'sqlite3',
        'src.app.routers.file',
        'src.app.routers.rag',
        'src.app.routers.chat',
        'src.app.routers.tags',
        'src.app.routers.search',
        'src.app.routers.workflows',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='UroborosKnowledgeHub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    spec_path = os.path.join(root_dir, "UroborosKnowledgeHub.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"Generated spec file: {spec_path}")

    build_spec_path = os.path.join(root_dir, "build", "UroborosKnowledgeHub.spec")
    with open(build_spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"Generated spec file: {build_spec_path}")

    return spec_path


generate_build_spec = create_spec_file


def build_executable(check_only=False):
    """Build the standalone desktop executable via PyInstaller or check spec."""
    spec_path = create_spec_file()
    if check_only:
        print("Spec check complete. Ready for PyInstaller compilation.")
        return True

    cmd = ["pyinstaller", "--clean", "--noconfirm", spec_path]
    print(f"Running build command: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=root_dir)
    return res.returncode == 0


if __name__ == "__main__":
    check = "--check-only" in sys.argv
    build_executable(check_only=check)
