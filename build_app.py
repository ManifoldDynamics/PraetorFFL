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
    f'--add-data=ffl_suite/assets/themes/modern_saas.json{separator}ffl_suite/assets/themes',
    '--collect-all=customtkinter',
    '--clean',
])
