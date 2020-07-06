#!/usr/bin/env python

import time
from math import *
import json
from pathlib import Path
import mimetypes
import threading
from loguru import logger
from functools import partialmethod
import sys
from pathlib import Path
import psutil
import os
from urllib.request import urlopen
import io
import pygame

import version.scenes.reload

class Queue():
    pass

# Constants
DEFAULTASSETPACKS = ['vanilla']

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

@logger.catch
def assetpacks(logger, pygame, screen, clock, assets, options, lang, windowsize, pressedkeys):
    def setoptions(curopt):
        logger.debug('Reloading "curopt.json"')
        h = []
        [h.append(i) for i in curopt['assetpacks'] if i not in h]
        curopt['assetpacks'] = h.copy()
        h = []
        for i in range(len(curopt['assetpacks'])):
            p = Path(curopt['assetpacks'][i])
            if p.parent.name == 'file':
                p = p.parent.parent / 'assetpacks' / p.name
                if p.is_dir():
                    h.append(curopt['assetpacks'][i])
                else:
                    logger.warning(f'Missing Loaded Assetpack "{curopt["assetpacks"][i]}". Skipping Missing File.')
            elif p.name in DEFAULTASSETPACKS:
                p = p.parent / 'version' / 'assets' / p.name
                if p.is_dir():
                    h.append(curopt['assetpacks'][i])
                else:
                    logger.warning(f'Missing Loaded Assetpack "{curopt["assetpacks"][i]}". Skipping Missing File.')
        curopt['assetpacks'] = h.copy()
        if 'vanilla' not in curopt['assetpacks']:
            curopt['assetpacks'].append('vanilla')
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
            json.dump(curopt, f, indent=4)
        return(curopt)

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

    logger.debug(f'Loaded Scene "assetpacks"')

    assetpacks = options['assetpacks']
    enabled = []
    if not (f := Path('assetpacks')).exists():
        f.mkdir()
    for i in options['assetpacks']:
        p = Path(i)
        if p.parent.name == 'file':
            p = p.parent.parent / 'assetpacks' / p.name
        elif p.name in DEFAULTASSETPACKS:
            p = p.parent / 'version' / 'assets' / p.name
        if p.is_dir():
            j = p / 'pack.json'
            if j.is_file():
                try:
                    k = json.load(open(j, 'r'))
                except json.decoder.JSONDecodeError:
                    k = {}
                enabled.append({
                    'name': i,
                    'description': '',
                    'author': ''
                })
                for l in k:
                    enabled[-1][l] = k[l]
            else:
                enabled.append({
                    'name': i,
                    'description': '',
                    'author': ''
                })
            try:
                enabled[-1]['icon'] = pygame.image.load(str(p / 'icon.png'))
            except pygame.error:
                enabled[-1]['icon'] = getasset('textures.menu.unknownicon', assets).copy()
            enabled[-1]['path'] = i
    disabled = []
    for i in (Path('version') / 'assets').iterdir():
        if i.is_dir():
            isenabled = False
            for j in enabled:
                if i.name == j['path']:
                    isenabled = True
            if not isenabled:
                j = i / 'pack.json'
                if j.is_file():
                    try:
                        k = json.load(open(j, 'r'))
                    except json.decoder.JSONDecodeError:
                        k = {}
                    disabled.append({
                        'name': i.name,
                        'description': '',
                        'author': ''
                    })
                    for l in k:
                        if isinstance(k[l], str):
                            disabled[-1][l] = k[l]
                else:
                    disabled.append({
                        'name': f'file/{i.name}',
                        'description': '',
                        'author': ''
                    })
                try:
                    disabled[-1]['icon'] = pygame.image.load(str(i / 'icon.png'))
                except pygame.error:
                    disabled[-1]['icon'] = getasset('textures.menu.unknownicon', assets).copy()
                disabled[-1]['path'] = i.name
    for i in Path('assetpacks').iterdir():
        if i.is_dir():
            isenabled = False
            for j in enabled:
                if f'file/{i.name}' == j['path']:
                    isenabled = True
            if not isenabled:
                j = i / 'pack.json'
                if j.is_file():
                    try:
                        k = json.load(open(j, 'r'))
                    except json.decoder.JSONDecodeError:
                        k = {}
                    disabled.append({
                        'name': i.name,
                        'description': '',
                        'author': ''
                    })
                    for l in k:
                        if isinstance(k[l], str):
                            disabled[-1][l] = k[l]
                else:
                    disabled.append({
                        'name': f'file/{i.name}',
                        'description': '',
                        'author': ''
                    })
                try:
                    disabled[-1]['icon'] = pygame.image.load(str(i / 'icon.png'))
                except pygame.error:
                    disabled[-1]['icon'] = getasset('textures.menu.unknownicon', assets).copy()
                disabled[-1]['path'] = f'file/{i.name}'

    end = False
    changed = False
    disabledscroll = 0
    enabledscroll = 0
    disabledscrollvel = 0
    enabledscrollvel = 0
    while not end:
        resize = False
        # Mouse Pos
        mousepos = pygame.mouse.get_pos()
        # Button Size
        button = getasset('textures.menu.buttons', assets)[4]
        buttonsize = list(button.get_rect().size)
        maxbuttonsize = (windowsize[0] / 4, windowsize[1] / 14)
        buttonsize[1] = buttonsize[1] * (maxbuttonsize[0] / buttonsize[0])
        buttonsize[0] = maxbuttonsize[0]
        if buttonsize[1] > maxbuttonsize[1]:
            buttonsize[0] = buttonsize[0] * (maxbuttonsize[1] / buttonsize[1])
            buttonsize[1] = maxbuttonsize[1]
        buttonsize = (round(buttonsize[0]), round(buttonsize[1]))
        # Title Size
        title = getasset('textures.menu.minigamelobby', assets).copy()
        titlesize = list(title.get_rect().size)
        maxtitlesize = (windowsize[0] / 1.25, windowsize[1] / 4)
        titlesize[1] = titlesize[1] * (maxtitlesize[0] / titlesize[0])
        titlesize[0] = maxtitlesize[0]
        if titlesize[1] > maxtitlesize[1]:
            titlesize[0] = titlesize[0] * (maxtitlesize[1] / titlesize[1])
            titlesize[1] = maxtitlesize[1]
        titlesize = (round(titlesize[0]), round(titlesize[1]))
        # Menu Size
        menusize = (round(windowsize[0] / 2 - 30), round(windowsize[1] / 2 + buttonsize[1] * 5 - round(windowsize[1] / 10 + titlesize[1] + 10) - 10))
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
                if event.key == pygame.K_t and (pygame.K_F3 in pressedkeys):
                    sentlogs = []
                    lang, assets = loadassets(options)
                elif event.key == pygame.K_c and (pygame.K_F3 in pressedkeys):
                    logger.warning('Crashing In 3..')
                    crash = [time.time() + 1, time.time() + 2, time.time() + 3]
                elif event.key == pygame.K_F4 and (pygame.K_LALT in pressedkeys):
                    return(True)
                elif event.key == pygame.K_ESCAPE:
                    end = True
                elif event.key == eval(f'pygame.K_{options["key.screenshot"]}'):
                    try:
                        getaudio('sounds.misc.screenshot', assets).play()
                    except AttributeError: pass
                    if not (f := Path('screenshots')).exists():
                        os.mkdir(f)
                    pygame.image.save(screen, f'screenshots/{time.strftime("%Y-%m-%d %H-%M-%S")}.jpg')
                    resize = True
                    screen.fill((255, 255, 255))
                elif event.key == pygame.K_SPACE:
                    changed = True
            elif event.type == pygame.KEYUP:
                try:
                    pressedkeys.remove(event.key)
                except KeyError: pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(2):
                        if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10) and mousepos[0] <= windowsize[0] / 2 - 10 + i % 2 * (buttonsize[0] + 10) and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * (5 + floor(i / 2)) + 10 * floor(i / 2) and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * (5 + floor(i / 2)) + 10 * floor(i / 2) + buttonsize[1]:
                            try:
                                getaudio('sounds.menu.click', assets).play()
                            except AttributeError: pass
                            if i == 0:
                                end = True
                            elif i == 1:
                                try:
                                    getaudio('sounds.music.menu', assets).fadeout(250)
                                except AttributeError: pass
                                queue = Queue()
                                queue.end = False
                                thread = threading.Thread(target=version.scenes.reload.reload, args=[pygame, screen, clock, assets, options, lang, windowsize, pressedkeys, queue])
                                thread.setDaemon(True)
                                thread.start()
                                options['assetpacks'] = []
                                for j in enabled:
                                    options['assetpacks'].append(j['path'])
                                options = setoptions(options)
                                lang, assets = loadassets(options)
                                time.sleep(1)
                                queue.end = True
                                end = True
                                thread.join()
                                try:
                                    windowsize, pressedkeys = queue.data
                                except AttributeError:
                                    return(True)
                                try:
                                    getasset('sounds.music.menu', assets).play(-1)
                                except AttributeError: pass
                elif event.button == 4:
                    if mousepos[0] >= 20 and mousepos[0] <= 20 + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                        disabledscrollvel += -6
                    if mousepos[0] >= round(windowsize[0] / 2 + 10) and mousepos[0] <= round(windowsize[0] / 2 + 10) + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                        enabledscrollvel += -6
                elif event.button == 5:
                    if mousepos[0] >= 20 and mousepos[0] <= 20 + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                        disabledscrollvel += 6
                    if mousepos[0] >= round(windowsize[0] / 2 + 10) and mousepos[0] <= round(windowsize[0] / 2 + 10) + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                        enabledscrollvel += 6

        # Display
        display = pygame.Surface(windowsize)
        display.set_alpha(100)

        # Background
        display.fill((0, 0, 0))
        tile = getasset('textures.menu.optionsbackground', assets).copy()
        tilesize = list(tile.get_rect().size)
        maxtilesize = (windowsize[0] / 10, windowsize[1] / 10)
        tilesize[1] = tilesize[1] * (maxtilesize[0] / tilesize[0])
        tilesize[0] = maxtilesize[0]
        if tilesize[1] > maxtilesize[1]:
            tilesize[0] = tilesize[0] * (maxtilesize[1] / tilesize[1])
            tilesize[1] = maxtilesize[1]
        tilesize = (round(tilesize[0]), round(tilesize[1]))
        tile = pygame.transform.scale(tile, tilesize)
        fits = (ceil(windowsize[0] / tilesize[0]), ceil(windowsize[1] / tilesize[1]))
        background = pygame.Surface((tilesize[0] * fits[0], tilesize[1] * fits[1]))
        for i in range(fits[0]):
            for j in range(fits[1]):
                background.blit(tile, (tilesize[0] * i, tilesize[1] * j))
        display.blit(background, (windowsize[0] / 2 - tilesize[0] * fits[0] / 2, windowsize[1] / 2 - tilesize[1] * fits[1] / 2))
        vignette = getasset('textures.misc.vignette', assets).copy()
        vignette = pygame.transform.scale(vignette, (windowsize[0], windowsize[1]))
        display.blit(vignette, (0, 0))

        # Title
        title = pygame.transform.scale(title, titlesize)
        display.blit(title, (round(windowsize[0] / 2 - titlesize[0] / 2), round(windowsize[1] / 10)))

        subtitle = getasset('textures.menu.totobirdcreations', assets).copy()
        subtitlesize = list(subtitle.get_rect().size)
        maxsubtitleheight = titlesize[1] / 2.5
        subtitlesize[0] = subtitlesize[0] * (maxsubtitleheight / subtitlesize[1])
        subtitlesize[1] = maxsubtitleheight
        subtitlesize = (round(subtitlesize[0]), round(subtitlesize[1]))
        subtitle = pygame.transform.scale(subtitle, subtitlesize)
        display.blit(subtitle, (round(windowsize[0] / 2 - subtitlesize[0] / 2), round(windowsize[1] / 10 + titlesize[1] - subtitlesize[1])))

        # Buttons
        button = pygame.transform.scale(button, buttonsize)

        hbutton = getasset('textures.menu.buttons', assets)[5]
        hbuttonsize = (round(buttonsize[0]), round(buttonsize[1]))
        hbutton = pygame.transform.scale(hbutton, hbuttonsize)

        for i in range(2):
            if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10) and mousepos[0] <= windowsize[0] / 2 - 5 + i % 2 * (buttonsize[0] + 10) and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * (5 + floor(i / 2)) + 10 * floor(i / 2) and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * (5 + floor(i / 2)) + 10 * floor(i / 2) + buttonsize[1]:
                display.blit(hbutton, (windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10), windowsize[1] / 2 + buttonsize[1] * (5 + floor(i / 2)) + 10 * floor(i / 2)))
            else:
                display.blit(button, (windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10), windowsize[1] / 2 + buttonsize[1] * (5 + floor(i / 2)) + 10 * floor(i / 2)))
            if i < 1:
                l = getlang(f'assetpacksmenu.buttons_{i}', lang)
            elif i == 1:
                if changed:
                    l = getlang(f'assetpacksmenu.buttons_{i + 1}', lang)
                    buttontext = colouredtext(splitcolours(l), getfont('font', assets))
                else:
                    l = getlang(f'assetpacksmenu.buttons_{i}', lang)
                    buttontext = colouredtext(splitcolours(l), getfont('font', assets))
            else:
                l = getlang(f'assetpacksmenu.buttons_{i + 1}', lang)
            buttontext = colouredtext(splitcolours(l), getfont('font', assets))
            buttontextsize = list(buttontext.get_rect().size)
            buttontextsize[0] = buttontextsize[0] * (buttonsize[1] / 2 / buttontextsize[1])
            buttontextsize[1] = buttonsize[1] / 2
            buttontextsize = (round(buttontextsize[0]), round(buttontextsize[1]))
            buttontext = pygame.transform.scale(buttontext, buttontextsize)

            display.blit(buttontext, (windowsize[0] / 2 - buttonsize[0] / 2 - 5 + i % 2 * (buttonsize[0] + 10) - buttontextsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * (5 + floor(i / 2)) + 10 * floor(i / 2) + buttontextsize[1] / 2))

        # Menus
        menu = pygame.Surface(menusize, pygame.SRCALPHA)
        menu.fill((0, 0, 0, 175))
        menudisabled = menu.copy()
        disabledlist = pygame.Surface((menusize[0], 110 * len(disabled) + 10), pygame.SRCALPHA)
        newdisabled = disabled.copy()
        newenabled = enabled.copy()
        for i in range(len(disabled)):
            if mousepos[0] >= 25 and mousepos[0] <= 25 + menusize[0] - 10 and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll + 109:
                if mousepos[0] >= 20 and mousepos[0] <= 20 + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                    pygame.draw.rect(disabledlist, (255, 255, 255, 127), pygame.Rect(5, 110 * i + 5, menusize[0] - 10, 110))
            if disabled[i]['path'] == 'vanilla':
                colour = (85, 255, 85)
            elif disabled[i]['path'].startswith('file/'):
                colour = (255, 255, 255)
            else:
                colour = (255, 170, 0)
            name = colouredtext([{'text': disabled[i]['name'], 'colour': colour}], getfont('font', assets))
            namesize = list(name.get_rect().size)
            namesize[0] = namesize[0] * (28 / namesize[1])
            namesize[1] = 28
            namesize = (round(namesize[0]), round(namesize[1]))
            name = pygame.transform.scale(name, namesize)
            disabledlist.blit(name, (110, 110 * i + 15))
            desc = colouredtext(splitcolours('§7  ' + disabled[i]['description'].replace('§r', '§7')), getfont('font', assets))
            descsize = list(desc.get_rect().size)
            descsize[0] = descsize[0] * (28 / descsize[1])
            descsize[1] = 28
            descsize = (round(descsize[0]), round(descsize[1]))
            desc = pygame.transform.scale(desc, descsize)
            desc = pygame.transform.scale(desc, descsize)
            disabledlist.blit(desc, (110, 110 * i + 43))
            athr = colouredtext(splitcolours('§8  ' + disabled[i]['author'].replace('§r', '§8')), getfont('font', assets))
            athrsize = list(athr.get_rect().size)
            athrsize[0] = athrsize[0] * (28 / athrsize[1])
            athrsize[1] = 28
            athrsize = (round(athrsize[0]), round(athrsize[1]))
            athr = pygame.transform.scale(athr, athrsize)
            athr = pygame.transform.scale(athr, athrsize)
            disabledlist.blit(athr, (110, 110 * i + 71))
            icon = disabled[i]['icon'].copy()
            icon = pygame.transform.scale(icon, (90, 90))
            disabledlist.blit(icon, (15, 110 * i + 15))
            if mousepos[0] >= 25 and mousepos[0] <= 25 + menusize[0] - 10 and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll + 109:
                if mousepos[0] >= 20 and mousepos[0] <= 20 + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                    right = getasset('textures.menu.arrowbuttons.right_hover', assets)
                    right = pygame.transform.scale(right, (90, 90))
                    disabledlist.blit(right, (15, 110 * i + 15))
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                try:
                                    getaudio('sounds.menu.click', assets).play()
                                except AttributeError: pass
                                newenabled.insert(0, disabled[i])
                                del newdisabled[i]
            pygame.draw.rect(disabledlist, (0, 0, 0), pygame.Rect(5, 110 * i + 5, menusize[0] - 10, 110), 10)
        menudisabled.blit(disabledlist, (0, 0 - disabledscroll))
        menuenabled = menu.copy()
        enabledlist = pygame.Surface((menusize[0], 110 * len(enabled) + 10), pygame.SRCALPHA)
        for i in range(len(enabled)):
            if mousepos[0] >= round(windowsize[0] / 2 + 10) and mousepos[0] <= round(windowsize[0] / 2 + 10) + menusize[0] - 10 and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll + 109:
                if mousepos[0] >= round(windowsize[0] / 2 + 10) and mousepos[0] <= round(windowsize[0] / 2 + 10) + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 9) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 9) + menusize[1]:
                    pygame.draw.rect(enabledlist, (255, 255, 255, 127), pygame.Rect(5, 110 * i + 5, menusize[0] - 10, 110))
            if enabled[i]['path'] == 'vanilla':
                colour = (85, 255, 85)
            elif enabled[i]['path'].startswith('file/'):
                colour = (255, 255, 255)
            else:
                colour = (255, 170, 0)
            name = colouredtext([{'text': enabled[i]['name'], 'colour': colour}], getfont('font', assets))
            namesize = list(name.get_rect().size)
            namesize[0] = namesize[0] * (28 / namesize[1])
            namesize[1] = 28
            namesize = (round(namesize[0]), round(namesize[1]))
            name = pygame.transform.scale(name, namesize)
            enabledlist.blit(name, (110, 110 * i + 15))
            desc = colouredtext(splitcolours('§7  ' + enabled[i]['description'].replace('§r', '§7')), getfont('font', assets))
            descsize = list(desc.get_rect().size)
            descsize[0] = descsize[0] * (28 / descsize[1])
            descsize[1] = 28
            descsize = (round(descsize[0]), round(descsize[1]))
            desc = pygame.transform.scale(desc, descsize)
            desc = pygame.transform.scale(desc, descsize)
            enabledlist.blit(desc, (110, 110 * i + 43))
            athr = colouredtext(splitcolours('§8  ' + enabled[i]['author'].replace('§r', '§8')), getfont('font', assets))
            athrsize = list(athr.get_rect().size)
            athrsize[0] = athrsize[0] * (28 / athrsize[1])
            athrsize[1] = 28
            athrsize = (round(athrsize[0]), round(athrsize[1]))
            athr = pygame.transform.scale(athr, athrsize)
            athr = pygame.transform.scale(athr, athrsize)
            enabledlist.blit(athr, (110, 110 * i + 71))
            icon = enabled[i]['icon'].copy()
            icon = pygame.transform.scale(icon, (90, 90))
            enabledlist.blit(icon, (15, 110 * i + 15))
            if mousepos[0] >= round(windowsize[0] / 2 + 10) and mousepos[0] <= round(windowsize[0] / 2 + 10) + menusize[0] - 10 and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 5 - disabledscroll + 109:
                if mousepos[0] >= round(windowsize[0] / 2 + 10) and mousepos[0] <= round(windowsize[0] / 2 + 10) + menusize[0] and mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                    if i >= 1:
                        up = getasset('textures.menu.arrowbuttons.up', assets)
                        up = pygame.transform.scale(up, (90, 90))
                        enabledlist.blit(up, (15, 110 * i + 15))
                    if i <= len(enabled) - 2:
                        down = getasset('textures.menu.arrowbuttons.down', assets)
                        down = pygame.transform.scale(down, (90, 90))
                        enabledlist.blit(down, (15, 110 * i + 15))
                    if enabled[i]['path'] != 'vanilla':
                        left = getasset('textures.menu.arrowbuttons.left', assets)
                        left = pygame.transform.scale(left, (90, 90))
                        enabledlist.blit(left, (15, 110 * i + 15))
                    if mousepos[0] >= round(windowsize[0] / 2 + 70) and mousepos[0] <= round(windowsize[0] / 2 + 160):
                        if mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * i + 20 - disabledscroll and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + 110 * (i + 0.5) - disabledscroll:
                            if i >= 1:
                                up = getasset('textures.menu.arrowbuttons.up_hover', assets)
                                up = pygame.transform.scale(up, (90, 90))
                                enabledlist.blit(up, (15, 110 * i + 15))
                                for event in events:
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        if event.button == 1:
                                            try:
                                                getaudio('sounds.menu.click', assets).play()
                                            except AttributeError: pass
                                            newenabled.insert(i - 1, newenabled.pop(i))
                        else:
                            if i <= len(enabled) - 2:
                                down = getasset('textures.menu.arrowbuttons.down_hover', assets)
                                down = pygame.transform.scale(down, (90, 90))
                                enabledlist.blit(down, (15, 110 * i + 15))
                                for event in events:
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        if event.button == 1:
                                            try:
                                                getaudio('sounds.menu.click', assets).play()
                                            except AttributeError: pass
                                            newenabled.insert(i + 1, newenabled.pop(i))
                    elif enabled[i]['path'] != 'vanilla':
                        left = getasset('textures.menu.arrowbuttons.left_hover', assets)
                        left = pygame.transform.scale(left, (90, 90))
                        enabledlist.blit(left, (15, 110 * i + 15))
                        for event in events:
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == 1:
                                    try:
                                        getaudio('sounds.menu.click', assets).play()
                                    except AttributeError: pass
                                    newdisabled.insert(0, enabled[i])
                                    del newenabled[i]
            pygame.draw.rect(enabledlist, (0, 0, 0), pygame.Rect(5, 110 * i + 5, menusize[0] - 10, 110), 10)
        menuenabled.blit(enabledlist, (0, 0 - enabledscroll))

        disabled = sorted(newdisabled.copy(), key=lambda k: k['name'], reverse=True)
        enabled = newenabled.copy()

        enabledpaths = []
        for j in enabled:
            enabledpaths.append(j['path'])
        if enabledpaths == options['assetpacks']:
            changed = False
        else:
            changed = True

        # Scroll Bars
        try:
            pygame.draw.rect(
                menudisabled,
                (150, 150, 150),
                pygame.Rect(
                    menusize[0] - 15,
                    round(menusize[1] * (disabledscroll / (110 * len(disabled)))),
                    15,
                    round(menusize[1] / len(disabled))
                )
            )
        except ZeroDivisionError:
            pygame.draw.rect(
                menudisabled,
                (150, 150, 150),
                pygame.Rect(
                    menusize[0] - 15,
                    0,
                    15,
                    menusize[1]
                )
            )
        try:
            pygame.draw.rect(
                menuenabled,
                (150, 150, 150),
                pygame.Rect(
                    menusize[0] - 15,
                    round(menusize[1] * (enabledscroll / (110 * len(enabled)))),
                    15,
                    round(menusize[1] / len(enabled))
                )
            )
        except ZeroDivisionError:
            pygame.draw.rect(
                menuenabled,
                (150, 150, 150),
                pygame.Rect(
                    menusize[0] - 15,
                    0,
                    15,
                    menusize[1]
                )
            )

        # Menus
        display.blit(menudisabled, (20, round(windowsize[1] / 10 + titlesize[1] + 10)))
        display.blit(menuenabled, (round(windowsize[0] / 2 + 10), round(windowsize[1] / 10 + titlesize[1] + 10)))

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

        disabledscroll += disabledscrollvel * 5
        enabledscroll += enabledscrollvel * 5
        if disabledscrollvel > 0:
            disabledscrollvel -= 1
        if disabledscrollvel < 0:
            disabledscrollvel += 1
        if enabledscrollvel > 0:
            enabledscrollvel -= 1
        if enabledscrollvel < 0:
            enabledscrollvel += 1

        if disabledscroll < 0:
            disabledscroll = 0
            disabledscrollvel = 0
        if enabledscroll < 0:
            enabledscroll = 0
            enabledscrollvel = 0

        if disabledscroll > max([110 * (len(disabled) - 1), 0]):
            disabledscroll = max([110 * (len(disabled) - 1), 0])
            disabledscrollvel = 0
        if enabledscroll > max([110 * (len(enabled) - 1), 0]):
            enabledscroll = max([110 * (len(enabled) - 1), 0])
            enabledscrollvel = 0

    return((assets, options, lang, windowsize, pressedkeys))