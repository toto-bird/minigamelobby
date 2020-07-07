#!/usr/bin/env python

import subprocess

version = 'a00'

subprocess.call(['pip3', 'install', '-r', f'requirements_{version}.txt'])

from pathlib import Path
from path import Path as usepath
import os
import zipfile
import requests
import shutil
from appdirs import *

f = Path(user_data_dir('MinigameLobby', 'TotobirdCreations'))
try:
    if not f.is_dir():
        os.mkdir(f)
except FileExistsError:
    print(f'Failed To Create Folder "{f}". Please Remove It And Try Again.')
with usepath(f):
    fi = f / 'assetpacks'
    if not fi.is_dir():
        os.mkdir(fi)
    url = 'https://github.com/toto-bird/minigamelobby/archive/master.zip'
    file = Path('minigamelobby-master.zip')
    fw = requests.get(url)
    open(file, 'wb').write(fw.content)
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall('.')
    direc = Path('minigamelobby-master')
    shutil.move(direc / 'reinstall.py', f / './reinstall.py')
    vdirec = Path('version')
    try:
        shutil.rmtree(vdirec)
    except FileNotFoundError: pass
    shutil.move(direc / 'version', f / 'version')
    shutil.rmtree(direc)
    file.unlink()

    import version.scenes.main