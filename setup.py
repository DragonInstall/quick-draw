from setuptools import setup

APP = ['src/mainUI.py']
DATA_FILES = []
# py2app options
OPTIONS = {
    'argv_emulation': False, # Keep False for Tkinter stability
    'packages': ['customtkinter', 'PIL', 'tkinter'],
    'plist': {
        'CFBundleName': 'Quick Sketcher',
        'CFBundleDisplayName': 'Quick Sketcher',
        'CFBundleGetInfoString': "Timed reference viewer",
        'CFBundleIdentifier': "com.yourname.quicksketcher",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    name='Quick Sketcher',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)