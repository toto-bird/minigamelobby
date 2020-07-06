#!/usr/bin/env python

import subprocess
from path import Path
import requests
import zipfile
import shutil
import pathlib

with Path(__file__).parent:
    print('Installing Python Packages')
    packages = [
        'json5',
        'loguru',
        'psutil',
        'urllib3',
        'pygame'
    ]

    command = ['python', '-m', 'pip', 'install']
    for i in packages:
        command.append(i)
    subprocess.call(command)

    print('Fetching Files')

    url = 'https://github.com/toto-bird/minigamelobby/archive/master.zip'
    file = Path('minigamelobby-master.zip')
    f = requests.get(url)
    open(file, 'wb').write(f.content)
    print('Unzipping Files')
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall('.')
    print('Relocating and Updating Files')
    direc = Path('minigamelobby-master')
    shutil.move(direc / 'minigamelobby.py', Path(__file__).parent / './minigamelobby.py')
    vdirec = Path('version')
    try:
        shutil.rmtree(vdirec)
    except FileNotFoundError: pass
    shutil.move(direc / 'version', Path(__file__).parent / 'version')
    shutil.rmtree(direc)
    file.unlink()
    try:
        Path('assetpacks').mkdir()
    except FileExistsError: pass
    print('Done')