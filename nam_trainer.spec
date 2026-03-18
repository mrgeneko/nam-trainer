# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for NAM Trainer
Build with: pyinstaller nam_trainer.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Get absolute paths
root_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(__file__).parent
neural_amp_dir = root_dir / "neural-amp-modeler"

a = Analysis(
    ['test_queue.py'],
    pathex=[str(Path(__file__).parent)],
    binaries=[],
    datas=[
        # Include neural-amp-modeler submodule
        ('neural-amp-modeler', 'neural-amp-modeler'),
        # Include local GUI overrides
        ('nam_trainer/gui/_resources', 'nam_trainer/gui/_resources'),
    ],
    hiddenimports=[
        # NAM imports
        'nam.train.core',
        'nam.models.metadata',
        'nam.models.metadata.GearType',
        'nam.models.metadata.ToneType',
        'nam.train.metadata',
        'nam.train.gui._resources.config',
        'nam.train.gui._resources.queue',
        'nam.train.gui._resources.queue_window',
        # Standard library tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # Other needed imports
        'json',
        'uuid',
        'threading',
        'subprocess',
        'pathlib',
        'datetime',
        're',
        'shutil',
        'tempfile',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',  # If not needed at runtime
        'scipy',
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
    name='NAMTrainer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Optional: add your own icon
    manifest=None,
    resources=[],
)

# For macOS .app bundle
app = BUNDLE(
    exe,
    name='NAMTrainer.app',
    icon='icon.icns',  # Optional: macOS icon
    bundle_identifier='com.namtrainer.app',
    info_plist={
        'CFBundleName': 'NAM Trainer',
        'CFBundleDisplayName': 'NAM Trainer',
        'CFBundleIdentifier': 'com.namtrainer.app',
        'CFBundleVersion': '1',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': 'NAMTrainer',
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
    },
)
