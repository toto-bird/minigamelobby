#!/usr/bin/env python

# Alpha
# Beta
# Release Candidate
# Official Release

###################################################
#               IMPORT DEPENDENCIES               #
###################################################
import pygame
import json
import requests
from urlpath import URL
import os
import os.path as path
from pathlib import Path
import sys
from loguru import logger
from functools import partialmethod
import mimetypes
import traceback
import time
from math import *
import signal
from multiprocessing import Process
import importlib.util as importlib
from urllib.request import urlopen
import io
import threading
import psutil

import version.scenes.options
import version.scenes.broken
import version.scenes.outdated
import version.scenes.unknown

class Queue():
    pass

###################################################
#              SETUP LOGGING SYSTEM               #
###################################################
logger.remove(0)
consoleformat = '<yellow>[</yellow><green>{time:YYYY-MM-DD HH:mm:ss}</green><yellow>]</yellow> <yellow>[</yellow><cyan>{module}</cyan><yellow>:</yellow><cyan>{line}</cyan><yellow>)] [</yellow><level>{level}</level><yellow>]</yellow> <level>{message}</level>'
fileformat = '[{time:YYYY-MM-DD HH:mm:ss}] [{module}:{line})] [{level}] {message}'
logger.add(
    sys.stderr,
    level=0,
    colorize=True,
    format=consoleformat
)
logger.add(
    'logs/{time:YYYY-MM-DD HH:mm:ss}.log',
    level=0,
    colorize=False,
    format=fileformat
)
if (f := Path('logs/latest.log')).exists():
    f.unlink()
logger.add(
    'logs/latest.log',
    level=0,
    colorize=False,
    format=fileformat
)
del logger.__class__.critical
logger.level("CHAT", no=0, color="<bold><dim><italic>")
logger.__class__.chat = partialmethod(logger.__class__.log, "CHAT")
logger.level("SIGNAL", no=20, color="<bold><dim><red>")
logger.__class__.signal = partialmethod(logger.__class__.log, "SIGNAL")
logger.level("FATAL", no=50, color="<white><RED><bold>")
logger.__class__.fatal = partialmethod(logger.__class__.log, "FATAL")
logger.level("MINIGAMELOBBY", no=50, color="<bold><white>")
logger.__class__.minigamelobby = partialmethod(logger.__class__.log, "MINIGAMELOBBY")

###################################################
#                   CONSTANTS                     #
###################################################
DEFAULTASSETPACKS = ['vanilla']

###################################################
#                   LOAD TOOLS                    #
###################################################
def handler(signum, frame):
    logger.signal(f'Signal {signal.Signals(signum).name} ({signum}) Received.')

def splitfilepath(file):
    folders = []
    while 1:
        file, folder = path.split(file)
        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(file)
            break
    folders.reverse()
    folders = list(filter(None, folders))
    return(folders)

def loadoptions(queue):
    logger.debug('Loading "Options.json"')
    options = {
        'maxfps': 60,
        'language': 'en',
        'assetpacks': ['vanilla'],
        'key.screenshot': 'F2'
    }
    try:
        j = json.load(open('./options.json', 'r'))
        for tag in j:
            if tag in options:
                if tag.startswith('key'):
                    try:
                        eval(f'pygame.K_{j[tag]}')
                        options[tag] = j[tag]
                    except AttributeError: pass
                else:
                    options[tag] = j[tag]
    except FileNotFoundError:
        logger.warning('Failed To Load "Options.json". Creating Missing File.')
    except json.decoder.JSONDecodeError:
        logger.warning('Failed To Load "Options.json". Replacing Corrupted File.')
    h = []
    [h.append(i) for i in options['assetpacks'] if i not in h]
    options['assetpacks'] = h.copy()
    h = []
    for i in range(len(options['assetpacks'])):
        p = Path(options['assetpacks'][i])
        if p.parent.name == 'file':
            p = p.parent.parent / 'assetpacks' / p.name
            if p.is_dir():
                h.append(options['assetpacks'][i])
            else:
                logger.warning(f'Missing Loaded Assetpack "{options["assetpacks"][i]}". Skipping Missing File.')
        elif p.name in DEFAULTASSETPACKS:
            p = p.parent / 'version' / 'assets' / p.name
            if p.is_dir():
                h.append(options['assetpacks'][i])
            else:
                logger.warning(f'Missing Loaded Assetpack "{options["assetpacks"][i]}". Skipping Missing File.')
    options['assetpacks'] = h.copy()
    if 'vanilla' not in options['assetpacks']:
        options['assetpacks'].append('vanilla')
    langexists = False
    for i in range(len(options['assetpacks'])):
        p = Path(options['assetpacks'][i])
        if p.parent.name == 'file':
            p = p.parent.parent / 'assetpacks' / p.name
            if p.is_dir():
                if (p / 'lang' / Path(f'{options["language"]}.json')).exists():
                    langexists = True
        elif p.name in DEFAULTASSETPACKS:
            p = p.parent / 'version' / 'assets' / p.name
            if p.is_dir():
                if (p / 'lang' / Path(f'{options["language"]}.json')).exists():
                    langexists = True
    if not langexists:
        logger.warning('Invalid Language Selected. Falling Back To "en".')
        if ('version/assets/vanilla/lang' / Path('en.json')).exists():
            options['language'] = 'en'
        else:
            logger.fatal('Language Fallback File "en.json" Missing. Please Rerun The Setup File In The Same Location.')
            queue.end = True
            exit(1)
    with open('./options.json', 'w') as f:
        json.dump(options, f, indent=4)
    return(options)

def loadassets(options):
    if not (f := Path('assetpacks')).exists():
        f.mkdir()
    assets = {}
    assetlist = []
    lang = {}
    logger.debug('Loading Languages')
    for i in reversed(options['assetpacks']):
        p = Path(i)
        if p.parent.name == 'file':
            p = p.parent.parent / 'assetpacks' / p.name
        elif p.name in DEFAULTASSETPACKS:
            p = p.parent / 'version' / 'assets' / p.name
        for j in p.rglob('*'):
            if j.is_file():
                if j not in assetlist:
                    assetlist.append(j)
        e = p / 'lang' / (options['language'] + '.json')
        try:
            f = json.load(open(e, 'r'))
            for j in f:
                lang[j] = f[j]
            if e.parent.parent.parent.name == 'assetpacks':
                logger.trace(f'Loaded "{Path("file") / e.parent.parent.name / e.parent.name / e.name}".')
            else:
                logger.trace(f'Loaded "{Path(e.parent.parent.name) / e.parent.name / e.name}".')
        except FileNotFoundError: pass
        except json.decoder.JSONDecodeError:
            if e.parts[0] == 'version':
                logger.warning(f'Failed To Load "{Path("/".join(e.parts[2:]))}". Skipping Corrupted File.')
            else:
                logger.warning(f'Failed To Load "{Path("file") / Path("/".join(e.parts[1:]))}". Skipping Corrupted File.')
    logger.debug('Loading Assets')
    for i in assetlist:
        mime = mimetypes.guess_type(i)[0]
        if mime == None:
            if i.parts[0] == 'version':
                j = i.relative_to('version/assets').with_suffix('')
                logger.warning(f'Failed To Load "{".".join(j.parts[1:])}". Skipping Unknown File (Unknown).')
            else:
                j = i.relative_to('assetpacks').with_suffix('')
                logger.warning(f'Failed To Load "{".".join(j.parts[1:])}". Skipping Unknown File (Unknown).')
        elif 'image' in mime:
            if i.parts[0] == 'version':
                j = i.relative_to('version/assets').with_suffix('')
                assets['.'.join(j.parts[1:])] = pygame.image.load(str(i))
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
            else:
                j = i.relative_to('assetpacks').with_suffix('')
                assets['.'.join(j.parts[1:])] = pygame.image.load(str(i))
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
        elif 'json' in mime:
            if i.parts[0] == 'version':
                j = i.relative_to('version/assets').with_suffix('')
                assets['.'.join(j.parts[1:])] = open(i, 'r')
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
            else:
                j = i.relative_to('assetpacks').with_suffix('')
                assets['.'.join(j.parts[1:])] = open(i, 'r')
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
        elif 'font' in mime:
            if i.parts[0] == 'version':
                j = i.relative_to('version/assets').with_suffix('')
                assets['.'.join(j.parts[1:])] = pygame.font.Font(str(i), 50)
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
            else:
                j = i.relative_to('assetpacks').with_suffix('')
                assets['.'.join(j.parts[1:])] = pygame.font.Font(str(i), 50)
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
        elif 'audio' in mime:
            if i.parts[0] == 'version':
                j = i.relative_to('version/assets').with_suffix('')
                assets['.'.join(j.parts[1:])] = pygame.mixer.Sound(str(i))
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
            else:
                j = i.relative_to('assetpacks').with_suffix('')
                assets['.'.join(j.parts[1:])] = pygame.mixer.Sound(str(i))
                logger.trace(f'Loaded "{".".join(j.parts[1:])}".')
        else:
            if i.parts[0] == 'version':
                j = i.relative_to('version/assets').with_suffix('')
                logger.warning(f'Failed To Load "{".".join(j.parts[1:])}". Skipping Unknown File ({mime}).')
            else:
                j = i.relative_to('assetpacks').with_suffix('')
                logger.warning(f'Failed To Load "{".".join(j.parts[1:])}". Skipping Unknown File ({mime}).')

    try:
        assets['textures.menu.totobirdcreations'] = pygame.image.load(io.BytesIO(urlopen('https://toto-bird.github.io/totobirdgames/totobirdcreations.png').read()))
    except:
        logger.error('Failed To Fetch Logo.')

    i = getasset('textures.menu.buttons', assets)
    isize = i.get_rect().size
    assets['textures.menu.buttons'] = (
        pygame.Surface((isize[0], floor(isize[1] / 6))),
        pygame.Surface((isize[0], floor(isize[1] / 6))),
        pygame.Surface((isize[0], floor(isize[1] / 6))),
        pygame.Surface((floor(isize[0] / 2), floor(isize[1] / 6))),
        pygame.Surface((floor(isize[0] / 2), floor(isize[1] / 6))),
        pygame.Surface((floor(isize[0] / 2), floor(isize[1] / 6)))
    )
    assets['textures.menu.buttons'][0].blit(i, (0, 0))
    assets['textures.menu.buttons'][1].blit(i, (0, 0 - floor(isize[1] / 6)))
    assets['textures.menu.buttons'][2].blit(i, (0, 0 - floor(isize[1] / 6) * 2))
    assets['textures.menu.buttons'][3].blit(i, (0, 0 - floor(isize[1] / 6) * 3))
    assets['textures.menu.buttons'][4].blit(i, (0, 0 - floor(isize[1] / 6) * 4))
    assets['textures.menu.buttons'][5].blit(i, (0, 0 - floor(isize[1] / 6) * 5))

    pygame.display.set_caption(getlang('window.title', lang).replace('{TITLE}', getlang('game.title', lang)).replace('{VERSION}', getlang('game.version', lang)))
    return((lang, assets))

# §
###########################################
##     |               ##     |          ##
##  0  |  Black        ##  a  |  Green   ##
##  1  |  Dark Blue    ##  b  |  Aqua    ##
##  2  |  Dark Green   ##  c  |  Red     ##
##  3  |  Dark Aqua    ##  d  |  Pink    ##
##  4  |  Dark Red     ##  e  |  Yellow  ##
##  5  |  Dark Purple  ##  f  |  White   ##
##  6  |  Gold         ##     |          ##
##  7  |  Gray         ####################
##  8  |  Dark Gray    ##
##  9  |  Blue         ##
##     |               ##
#########################

def splitcolours(text):
    ret = []
    split = False
    defcur = {
        'text': '',
        'colour': (255, 255, 255)
    }
    cur = defcur.copy()
    for i in text:
        if split:
            if i == '§':
                cur['text'] += i
            elif i == '0':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (0, 0, 0)
            elif i == '1':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (0, 0, 170)
            elif i == '2':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (0, 170, 0)
            elif i == '3':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (0, 170, 170)
            elif i == '4':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (170, 0, 0)
            elif i == '5':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (170, 0, 170)
            elif i == '6':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (255, 170, 0)
            elif i == '7':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (170, 170, 170)
            elif i == '8':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (85, 85, 85)
            elif i == '9':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (85, 85, 255)
            elif i == 'a':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (85, 255, 85)
            elif i == 'b':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (85, 255, 255)
            elif i == 'c':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (255, 85, 85)
            elif i == 'd':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (255, 85, 255)
            elif i == 'e':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (255, 255, 85)
            elif i == 'f':
                ret.append(cur)
                cur = defcur.copy()
                cur['colour'] = (255, 255, 255)
            elif i == 'r':
                ret.append(cur)
                cur = defcur.copy()
            else:
                cur['text'] += f'§{i}'
            split = False
        else:
            if i == '§':
                split = True
            else:
                cur['text'] += i
    ret.append(cur)
    return(ret)

def colouredtext(format, font):
    cur = []
    totalwidth = 0
    height = 0
    for i in format:
        r = font.render(i['text'], False, i['colour'])
        rsize = r.get_rect().size
        cur.append((r, rsize))
        totalwidth += rsize[0]
        if rsize[1] > height:
            height = rsize[1]
    width = 0
    ret = pygame.Surface((totalwidth, height), pygame.SRCALPHA)
    for i in cur:
        ret.blit(i[0], (width, 0))
        width += i[1][0]
    return(ret)

###################################################
#                      GAME                       #
###################################################
sentlogs = []
bugsurface = pygame.Surface((16, 16))
pygame.draw.rect(bugsurface, (255, 0, 255), pygame.Rect(8, 0, 8, 8))
pygame.draw.rect(bugsurface, (255, 0, 255), pygame.Rect(0, 8, 8, 8))
def getasset(name, assets):
    try:
        return(assets[name])
    except KeyError:
        if f'Failed To Load Asset "{name}"' not in sentlogs:
            logger.error(f'Failed To Load Asset "{name}"')
            sentlogs.append(f'Failed To Load Asset "{name}"')
        return(bugsurface)
def getaudio(name, assets):
    try:
        return(assets[name])
    except KeyError:
        if f'Failed To Load Sound "{name}"' not in sentlogs:
            logger.error(f'Failed To Load Sound "{name}"')
            sentlogs.append(f'Failed To Load Sound "{name}"')
        return(None)
def getfont(name, assets):
    try:
        return(assets[f'fonts.{name}'])
    except KeyError:
        if f'Failed To Load Font "{name}"' not in sentlogs:
            logger.error(f'Failed To Load Font "{name}"')
            sentlogs.append(f'Failed To Load Font "{name}"')
        return(pygame.font.SysFont('Comic Sans', 50))
def getlang(name, lang):
    try:
        return(lang[name])
    except KeyError:
        if f'Failed To Load Lang "{name}"' not in sentlogs:
            logger.error(f'Failed To Load Lang "{name}"')
            sentlogs.append(f'Failed To Load Lang "{name}"')
        return(name)

def loadscreen(pygame, screen, clock, assets, windowsize, queue):
    pressedkeys = set()
    def tick():
        lentime = time.time() + 0.05
        cpupercentage = psutil.cpu_percent() / 100
        rampercentage = psutil.virtual_memory().percent / 100
        return((lentime, cpupercentage, rampercentage))
    lentime, cpupercentage, rampercentage = tick()
    while not queue.end:
        if time.time() >= lentime:
            lentime, cpupercentage, rampercentage = tick()
        resize = False
        # Mouse Pos
        mousepos = pygame.mouse.get_pos()
        # General Events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return(True)
            elif event.type == pygame.VIDEORESIZE:
                windowsize = (event.w, event.h)
                screen = pygame.display.set_mode(windowsize, pygame.RESIZABLE|pygame.DOUBLEBUF)
                resize = True
            elif event.type == pygame.KEYDOWN:
                pressedkeys.add(event.key)
                if event.key == pygame.K_F2:
                    try:
                        getaudio('sounds.misc.screenshot', assets).play()
                    except AttributeError: pass
                    if not (f := Path('screenshots')).exists():
                        os.mkdir(f)
                    pygame.image.save(screen, f'screenshots/{time.strftime("%Y-%m-%d %H-%M-%S")}.jpg')
                    resize = True
                    screen.fill((255, 255, 255))
            elif event.type == pygame.KEYUP:
                try:
                    pressedkeys.remove(event.key)
                except KeyError: pass

        # Display
        display = pygame.Surface(windowsize)
        display.set_alpha(100)

        display.fill((36, 219, 131))

        # Title
        title = getasset('textures.menu.totobirdcreations', assets).copy()
        titlesize = list(title.get_rect().size)
        maxtitlesize = (windowsize[0] / 1.25, windowsize[1] / 4)
        titlesize[1] = titlesize[1] * (maxtitlesize[0] / titlesize[0])
        titlesize[0] = maxtitlesize[0]
        if titlesize[1] > maxtitlesize[1]:
            titlesize[0] = titlesize[0] * (maxtitlesize[1] / titlesize[1])
            titlesize[1] = maxtitlesize[1]
        titlesize = (round(titlesize[0]), round(titlesize[1]))
        title = pygame.transform.scale(title, titlesize)
        display.blit(title, (round(windowsize[0] / 2 - titlesize[0] / 2), round(windowsize[1] / 2 - titlesize[1] / 2)))

        # Display On Screen
        if not resize:
            screen.blit(display, (0, 0))

        pygame.display.flip()
        clock.tick(120)

    queue.data = (windowsize, pressedkeys)

@logger.catch
def main():
    logger.debug('Starting Up Game')

    pygame.init()
    pygame.font.init()

    ###################################################
    #             CREATE AND LOAD SCREEN              #
    ###################################################
    logger.success('Game Started')
    minwindowsize = (854, 480)
    windowsize = (round(854 * 1.5), round(480 * 1.5))
    screen = pygame.display.set_mode(minwindowsize, pygame.DOUBLEBUF)
    screen = pygame.display.set_mode(windowsize, pygame.RESIZABLE|pygame.DOUBLEBUF)
    clock = pygame.time.Clock()

    ###################################################
    #                   LOAD ASSETS                   #
    ###################################################

    assets = {
        'textures.menu.totobirdcreations': pygame.image.load(io.BytesIO(urlopen('https://toto-bird.github.io/totobirdgames/totobirdcreations.png').read()))
    }

    gamecompany = 'Totobird Creations'
    gametitle = 'Minigame Lobby'
    gameversion = 'a00'
    queue = Queue()
    queue.end = False
    thread = threading.Thread(target=loadscreen, args=[pygame, screen, clock, assets, windowsize, queue])
    thread.setDaemon(True)
    thread.start()
    options = loadoptions(queue)
    lang, assets = loadassets(options)
    #time.sleep(10)
    queue.end = True
    thread.join()
    try:
        windowsize, pressedkeys = queue.data
    except AttributeError:
        return(True)

    logger.minigamelobby('###################################################')
    logger.minigamelobby('##                                               ##')
    logger.minigamelobby(f'##{(gametitle + " - " + gameversion).center(47, " ")}##')
    logger.minigamelobby(f'##{gamecompany.center(47, " ")}##')
    logger.minigamelobby('##                                               ##')
    logger.minigamelobby('###################################################')
    ###################################################
    #                  GET WEB DATA                   #
    ###################################################

    website = URL('https://toto-bird.github.io/totobirdgames')
    rawwebsite = URL('https://raw.githubusercontent.com/toto-bird/totobirdgames/master')
    gameid = 'minigamelobby'

    try:
        webinfo = json.loads(str(requests.get(rawwebsite / 'versions.json').content)[2:-1].replace('\\n', ''))[gameid]
        if gameversion in webinfo['broken']:
            version.scenes.broken.broken(logger, pygame, screen, clock, assets, options, lang, windowsize)
            logger.debug(f'Unloaded Scene "broken"')
            return(2)
        elif gameversion != webinfo['version']:
            try:
                assets, options, lang, windowsize = version.scenes.outdated.outdated(logger, pygame, screen, clock, assets, options, lang, windowsize, webinfo['version'])
                logger.debug(f'Unloaded Scene "outdated"')
            except TypeError:
                logger.debug(f'Unloaded Scene "outdated"')
                return(0)
    except:
        try:
            assets, options, lang, windowsize = version.scenes.unknown.unknown(logger, pygame, screen, clock, assets, options, lang, windowsize)
            logger.debug(f'Unloaded Scene "unknown"')
        except TypeError:
            return(0)
            logger.debug(f'Unloaded Scene "unknown"')

    ###################################################
    #                  CHECK VERSION                  #
    ###################################################


    ###################################################
    #                   GAME LOOP                     #
    ###################################################
    pressedkeys = set()
    panoramatick = 0
    logger.debug(f'Loaded Scene "main"')
    #try:
    #    getaudio('sounds.music.menu', assets).play(-1)
    #except AttributeError: pass
    while True:
        resize = False
        # Mouse Pos
        mousepos = pygame.mouse.get_pos()
        # Button Size
        button = getasset('textures.menu.buttons', assets)[1]
        buttonsize = list(button.get_rect().size)
        maxbuttonsize = (windowsize[0] / 2, windowsize[1] / 14)
        buttonsize[1] = buttonsize[1] * (maxbuttonsize[0] / buttonsize[0])
        buttonsize[0] = maxbuttonsize[0]
        if buttonsize[1] > maxbuttonsize[1]:
            buttonsize[0] = buttonsize[0] * (maxbuttonsize[1] / buttonsize[1])
            buttonsize[1] = maxbuttonsize[1]
        buttonsize = (round(buttonsize[0]), round(buttonsize[1]))
        # General Events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return(0)
            elif event.type == pygame.VIDEORESIZE:
                windowsize = (event.w, event.h)
                screen = pygame.display.set_mode(windowsize, pygame.RESIZABLE|pygame.DOUBLEBUF)
                resize = True
            elif event.type == pygame.KEYDOWN:
                pressedkeys.add(event.key)
                if event.key == pygame.K_t and (pygame.K_F3 in pressedkeys):
                    sentlogs = []
                    lang, assets = loadassets(options)
                elif event.key == pygame.K_c and (pygame.K_F3 in pressedkeys):
                    logger.warning('Crashing In 3..')
                    crash = [time.time() + 1, time.time() + 2, time.time() + 3]
                elif event.key == pygame.K_F4 and (pygame.K_LALT in pressedkeys):
                    return(0)
                elif event.key == eval(f'pygame.K_{options["key.screenshot"]}'):
                    try:
                        getaudio('sounds.misc.screenshot', assets).play()
                    except AttributeError: pass
                    if not (f := Path('screenshots')).exists():
                        os.mkdir(f)
                    pygame.image.save(screen, f'screenshots/{time.strftime("%Y-%m-%d %H-%M-%S")}.jpg')
                    resize = True
                    screen.fill((255, 255, 255))
            elif event.type == pygame.KEYUP:
                try:
                    pressedkeys.remove(event.key)
                except KeyError: pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(4):
                        if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + buttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * 1.25 * (i - 1) and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * 1.25 * (i - 1) + buttonsize[1]:
                            try:
                                getaudio('sounds.menu.click', assets).play()
                            except AttributeError: pass
                            if i == 2:
                                try:
                                    assets, options, lang, windowsize, pressedkeys = version.scenes.options.options(logger, pygame, screen, clock, assets, options, lang, windowsize, pressedkeys)
                                    logger.debug(f'Unloaded Scene "options"')
                                except TypeError:
                                    return(0)
                            elif i == 3:
                                return(0)

        # Display
        display = pygame.Surface(windowsize)
        display.set_alpha(100)

        # Panorama
        panoramaparts = []
        i = 0
        try:
            assets['textures.menu.background.panorama_0']
        except KeyError:
            try:
                if 'Failed To Load Asset "textures.menu.background.panorama_0' not in sentlogs:
                    logger.error('Failed To Load Asset "textures.menu.background.panorama_0')
            except UnboundLocalError:
                logger.error('Failed To Load Asset "textures.menu.background.panorama_0')
                sentlogs = []
            sentlogs.append('Failed To Load Asset "textures.menu.background.panorama_0')
            assets['textures.menu.background.panorama_0'] = bugsurface
        while True:
            try:
                panoramaparts.append(assets[f'textures.menu.background.panorama_{i}'])
                panoramasize = list(panoramaparts[-1].get_rect().size)
                panoramasize[0] = panoramasize[0] * (windowsize[1] / panoramasize[1])
                panoramasize[1] = windowsize[1]
                if panoramasize[0] < windowsize[0]:
                    panoramasize[1] = panoramasize[1] * (windowsize[0] / panoramasize[0])
                    panoramasize[0] = windowsize[0]
                panoramasize = (round(panoramasize[0]), round(panoramasize[1]))
                panoramaparts[-1] = pygame.transform.scale(panoramaparts[-1], panoramasize)
            except KeyError: break
            i += 1
        panorama = pygame.Surface(windowsize)
        totalwidth = 0
        i = 0
        while True:
            if totalwidth - panoramatick < windowsize[0]:
                totalwidth += panoramasize[0]
                panorama.blit(panoramaparts[i % len(panoramaparts)], (round(0 - panoramatick + panoramasize[0] * i), windowsize[1] / 2 - panoramasize[1] / 2))
            else:
                break
            i += 1

        panoramatick += (0.00005 * (pow(panoramasize[0], 1.25)))
        if panoramatick >= len(panoramaparts) * panoramasize[0]:
            panoramatick = 0

        panoramasize = panorama.get_rect().size
        display.blit(panorama, (windowsize[0] / 2 - panoramasize[0] / 2, 0))

        # Background
        vignette = getasset('textures.misc.vignette', assets).copy()
        vignette = pygame.transform.scale(vignette, (windowsize[0], windowsize[1]))
        display.blit(vignette, (0, 0))

        # Title
        title = getasset('textures.menu.minigamelobby', assets).copy()
        titlesize = list(title.get_rect().size)
        maxtitlesize = (windowsize[0] / 1.25, windowsize[1] / 4)
        titlesize[1] = titlesize[1] * (maxtitlesize[0] / titlesize[0])
        titlesize[0] = maxtitlesize[0]
        if titlesize[1] > maxtitlesize[1]:
            titlesize[0] = titlesize[0] * (maxtitlesize[1] / titlesize[1])
            titlesize[1] = maxtitlesize[1]
        titlesize = (round(titlesize[0]), round(titlesize[1]))
        title = pygame.transform.scale(title, titlesize)
        display.blit(title, (round(windowsize[0] / 2 - titlesize[0] / 2), round(windowsize[1] / 10)))

        logo = getasset('textures.menu.totobirdcreations', assets).copy()
        logosize = list(logo.get_rect().size)
        maxlogoheight = titlesize[1] / 2.5
        logosize[0] = logosize[0] * (maxlogoheight / logosize[1])
        logosize[1] = maxlogoheight
        logosize = (round(logosize[0]), round(logosize[1]))
        logo = pygame.transform.scale(logo, logosize)
        display.blit(logo, (round(windowsize[0] / 2 - logosize[0] / 2), round(windowsize[1] / 10 + titlesize[1] - logosize[1])))

        # Buttons
        button = pygame.transform.scale(button, buttonsize)

        hbutton = getasset('textures.menu.buttons', assets)[2]
        hbuttonsize = (round(buttonsize[0]), round(buttonsize[1]))
        hbutton = pygame.transform.scale(hbutton, hbuttonsize)

        for i in range(4):
            if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + buttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * 1.25 * (i - 1) and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * 1.25 * (i - 1) + buttonsize[1]:
                display.blit(hbutton, (windowsize[0] / 2 - buttonsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * 1.25 * (i - 1)))
            else:
                display.blit(button, (windowsize[0] / 2 - buttonsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * 1.25 * (i - 1)))
            buttontext = colouredtext(splitcolours(getlang(f'mainmenu.buttons_{i}', lang)), getfont('font', assets))
            buttontextsize = list(buttontext.get_rect().size)
            buttontextsize[0] = buttontextsize[0] * (buttonsize[1] / 2 / buttontextsize[1])
            buttontextsize[1] = buttonsize[1] / 2
            buttontextsize = (round(buttontextsize[0]), round(buttontextsize[1]))
            buttontext = pygame.transform.scale(buttontext, buttontextsize)

            display.blit(buttontext, (windowsize[0] / 2 - buttontextsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * 1.25 * (i - 1) + buttontextsize[1] / 2))

        # Tickrate Keys
        try:
            if time.time() > crash[2]:
                logger.warning('Release F3+C')
                while True:
                    events = pygame.event.get()
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            pressedkeys.add(event.key)
                        elif event.type == pygame.KEYUP:
                            try:
                                pressedkeys.remove(event.key)
                                if (not pygame.K_c in pressedkeys) and (not pygame.K_F3 in pressedkeys):
                                    raise Exception('Game Crashed By User.')
                            except KeyError: pass
            elif crash[1] != None and (time.time() > crash[1]):
                logger.warning('Crashing In 1..')
                crash[1] = None
            elif crash[0] != None and (time.time() > crash[0]):
                logger.warning('Crashing In 2..')
                crash[0] = None
            elif (not pygame.K_c in pressedkeys) or (not pygame.K_F3 in pressedkeys):
                logger.warning('Crash Cancelled..')
                del crash
        except NameError: pass

        # Display On Screen
        if not resize:
            screen.blit(display, (0, 0))
        pygame.display.flip()
        clock.tick(120)

signal.signal(signal.SIGINT, handler)
ret = main()
logger.debug(f'Unloaded Scene "main"')
if ret == 0:
    logger.success('Game Stopped')
elif ret == 2:
    logger.error('Game Stopped Due To Removed Version')
else:
    logger.error('Game Crashed')
    ret = 1

time.sleep(0.25)

pygame.display.init()
pygame.display.quit()
pygame.quit()

sys.exit(ret)