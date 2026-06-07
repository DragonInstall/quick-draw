from setuptools import setup

APP = ['src/quickDrawQT.py']
DATA_FILES = []
# py2app options
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PySide6'],
    'plist': {
        'CFBundleName': 'Quick Sketcher',
        'CFBundleDisplayName': 'Quick Sketcher',
        'CFBundleExecutable': 'Quick Sketcher',
        'CFBundlePackageType': 'APPL',
        'LSMinimumSystemVersion': '12.0.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
        'LSUIElement': False
    }
}

setup(
    app=APP,
    name='Quick Sketcher',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)