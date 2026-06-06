# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src/mainUI.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Quick Sketcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Quick Sketcher',
)
app = BUNDLE(
    exe,
    name='Quick Sketcher.app',
    icon=None,
    bundle_identifier='com.DragonInstall.quicksketcher',
    info_plist={
        'NSDesktopFolderUsageDescription': 'Quick Sketcher needs access to your Desktop to load reference images.',
        'NSDocumentsFolderUsageDescription': 'Quick Sketcher needs access to your Documents to load reference images.',
        'NSDownloadsFolderUsageDescription': 'Quick Sketcher needs access to your Downloads to load reference images.',
        'NSHighResolutionCapable': 'True'
    },
)
