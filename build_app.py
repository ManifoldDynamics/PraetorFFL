import PyInstaller.__main__
import os
import platform

separator = ';' if platform.system() == 'Windows' else ':'

PyInstaller.__main__.run([
    'ffl_suite/main.py',
    '--name=FFLSuite',
    '--onefile',
    '--windowed',
    f'--add-data=ffl_suite/database/schema.sql{separator}ffl_suite/database',
    '--clean',
])
