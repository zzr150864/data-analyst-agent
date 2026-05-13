# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for DataAnalyst.exe"""

block_cipher = None

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env', '.'),
        ('prompts/', 'prompts/'),
    ],
    hiddenimports=[
        'pandas',
        'matplotlib',
        'matplotlib.backends.backend_pdf',
        'numpy',
        'httpx',
        'httpcore',
        'PIL',
        'sqlalchemy',
        'pymysql',
        'docx',
        'docx2pdf',
        'sklearn',
        'plotly',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'unittest',
        'test',
        'pdb',
        'distutils',
    ],
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
    name='DataAnalyst',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
