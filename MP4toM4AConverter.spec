# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mp4_to_m4a_converter.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['moviepy', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'pytube', 'yt_dlp', 'tkinter', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.ttk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MP4toM4AConverter',
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
)
