"""
PyInstaller Standalone Desktop Executable Build Script.
Generates uroboros_engine.spec and builds single-file Windows desktop application.
"""
import os
import sys

def generate_build_spec():
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['know.py'],
    pathex=['.'],
    binaries=[],
    datas=[('src/assets', 'src/assets')],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'sqlite3',
        'src.app.routers.file',
        'src.app.routers.rag',
        'src.app.routers.chat',
        'src.app.routers.tags',
        'src.app.routers.search',
        'src.app.routers.workflows',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='uroboros_engine',
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
'''
    with open("uroboros_engine.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    print("Generated uroboros_engine.spec successfully.")

if __name__ == "__main__":
    generate_build_spec()
