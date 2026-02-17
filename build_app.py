import PyInstaller.__main__
import os
import platform

separator = ';' if platform.system() == 'Windows' else ':'

PyInstaller.__main__.run([
    'main_web.py',
    '--name=FFLSuiteWeb',
    '--onefile',
    '--windowed',
    '--add-data=ffl_suite/web/templates;ffl_suite/web/templates',
    '--add-data=ffl_suite/web/static;ffl_suite/web/static',
    f'--add-data=ffl_suite/database/schema.sql{separator}ffl_suite/database',
    f'--add-data=ffl_suite/assets/themes/modern_saas.json{separator}ffl_suite/assets/themes',
    '--collect-all=customtkinter',
    '--clean',
])
