from distutils.core import setup
import os
import py2exe

currentPath = os.path.abspath('.')

setup(
    windows = ["ttvChat.py"],
    data_files = [
        ('log', ['log\logPath']),
        ('', ['settings_default.ini','README.md']),
        
    ]
)

# command  'python p2exeSetup.py py2exe'