# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=[r'C:\Users\Administrator\Desktop\Neuro Alexander'],
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
    hooksconfig={},
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
