# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Common data files and dependencies for both executables
added_files = [
    ('README.md', '.'),
    ('sudoers_note.txt', '.')
]

# First executable - wlanReport.py
a = Analysis(
    ['wlanReport.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz_cli = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe_cli = EXE(
    pyz_cli,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='wlanReport',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Second executable - wlanReportGUI.py
b = Analysis(
    ['wlanReportGUI.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz_gui = PYZ(b.pure, b.zipped_data, cipher=block_cipher)

exe_gui = EXE(
    pyz_gui,
    b.scripts,
    b.binaries,
    b.zipfiles,
    b.datas,
    [],
    name='wlanReportGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
) 