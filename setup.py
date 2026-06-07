from setuptools import setup

APP = ['src/quickDrawQT.py']
DATA_FILES = []

# py2app options
OPTIONS = {
    'argv_emulation': False,

    # Force it to only include the specific UI modules you need
    'includes': [
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets'
    ],

    'excludes': [
        # The Heavyweights
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.QtQml',
        'PySide6.QtQuick',

        # Network & Data
        'PySide6.QtNetwork',
        'PySide6.QtSql',
        'PySide6.QtWebSockets',
        'PySide6.QtWebChannel',
        'PySide6.QtXml',

        # Media & Documents
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtTextToSpeech',

        # Hardware & Geography
        'PySide6.QtBluetooth',
        'PySide6.QtSensors',
        'PySide6.QtPositioning',
        'PySide6.QtLocation',
        'PySide6.QtNfc',
        'PySide6.QtSerialPort',
        'PySide6.QtSerialBus',
    ],

    'plist': {
        'CFBundleName': 'Quick Draw',
        'CFBundleDisplayName': 'Quick Draw',
        'CFBundleExecutable': 'Quick Draw',
        'CFBundlePackageType': 'APPL',
        'LSMinimumSystemVersion': '12.0.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
        'LSUIElement': False
    }
}

setup(
    app=APP,
    name='Quick Draw',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)