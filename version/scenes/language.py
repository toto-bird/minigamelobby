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
def language(logger, pygame, screen, clock, assets, options, lang, windowsize, pressedkeys):
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
        assetlist = set()
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
                    assetlist.add(j)
            try:
                e = p / 'lang' / (options['language'] + '.json')
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

    setoptions(options)

    languages = []
    codes = []
    for i in range(len(options['assetpacks'])):
        p = Path(options['assetpacks'][i])
        if p.parent.name == 'file':
            p = p.parent.parent / 'assetpacks' / p.name / 'lang'
            if p.is_dir():
                for j in p.iterdir():
                    if j.is_file():
                        f = json.load(open(j, 'r'))
                        if j.with_suffix('').name not in codes:
                            languages.append({
                                'language.name': 'Unnamed',
                                'language.region': False
                            })
                            for k in f:
                                if k.startswith('language.'):
                                    languages[-1][k] = f[k]
                            languages[-1]['language.code'] = j.with_suffix('').name
                            codes.append(j.with_suffix('').name)
        elif p.name in DEFAULTASSETPACKS:
            p = p.parent / 'version' / 'assets' / p.name / 'lang'
            if p.is_dir():
                for j in p.iterdir():
                    if j.is_file():
                        f = json.load(open(j, 'r'))
                        if j.with_suffix('').name not in codes:
                            languages.append({
                                'language.name': 'Unnamed',
                                'language.region': False
                            })
                            for k in f:
                                if k.startswith('language.'):
                                    languages[-1][k] = f[k]
                            languages[-1]['language.code'] = j.with_suffix('').name
                            codes.append(j.with_suffix('').name)

    end = False
    scroll = 0
    scrollvel = 0
    while not end:
        resize = False
        # Mouse Pos
        mousepos = pygame.mouse.get_pos()
        # Large Button Size
        lbutton = getasset('textures.menu.buttons', assets)[1]
        lbuttonsize = list(lbutton.get_rect().size)
        maxlbuttonsize = (windowsize[0] / 2, windowsize[1] / 14)
        lbuttonsize[1] = lbuttonsize[1] * (maxlbuttonsize[0] / lbuttonsize[0])
        lbuttonsize[0] = maxlbuttonsize[0]
        if lbuttonsize[1] > maxlbuttonsize[1]:
            lbuttonsize[0] = lbuttonsize[0] * (maxlbuttonsize[1] / lbuttonsize[1])
            lbuttonsize[1] = maxlbuttonsize[1]
        lbuttonsize = (round(lbuttonsize[0]), round(lbuttonsize[1]))
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
        menusize = (windowsize[0], round(windowsize[1] / 2 + lbuttonsize[1] * 5 - round(windowsize[1] / 10 + titlesize[1] + 10) - 10))
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
                    if mousepos[0] >= windowsize[0] / 2 - lbuttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + lbuttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 and mousepos[1] <= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 + lbuttonsize[1]:
                        try:
                            getaudio('sounds.menu.click', assets).play()
                        except AttributeError: pass
                        end = True
                elif event.button == 4:
                    if mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                        scrollvel -= 5
                elif event.button == 5:
                    if mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                        scrollvel += 5

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
        lbutton = pygame.transform.scale(lbutton, lbuttonsize)

        hlbutton = getasset('textures.menu.buttons', assets)[2]
        hlbuttonsize = (round(lbuttonsize[0]), round(lbuttonsize[1]))
        hlbutton = pygame.transform.scale(hlbutton, hlbuttonsize)

        if mousepos[0] >= windowsize[0] / 2 - lbuttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + lbuttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 and mousepos[1] <= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 + lbuttonsize[1]:
            display.blit(hlbutton, (windowsize[0] / 2 - lbuttonsize[0] / 2, windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4))
        else:
            display.blit(lbutton, (windowsize[0] / 2 - lbuttonsize[0] / 2, windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4))
        lbuttontext = colouredtext(splitcolours(getlang(f'languagemenu.buttons_0', lang)), getfont('font', assets))
        lbuttontextsize = list(lbuttontext.get_rect().size)
        lbuttontextsize[0] = lbuttontextsize[0] * (lbuttonsize[1] / 2 / lbuttontextsize[1])
        lbuttontextsize[1] = lbuttonsize[1] / 2
        lbuttontextsize = (round(lbuttontextsize[0]), round(lbuttontextsize[1]))
        lbuttontext = pygame.transform.scale(lbuttontext, lbuttontextsize)

        display.blit(lbuttontext, (windowsize[0] / 2 - lbuttontextsize[0] / 2, windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 + lbuttontextsize[1] / 2))

        # Menus
        menu = pygame.Surface(menusize, pygame.SRCALPHA)
        menu.fill((0, 0, 0, 175))
        langlist = pygame.Surface((menusize[0], 40 * len(languages)), pygame.SRCALPHA)
        for i in range(len(languages)):
            if mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                if mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10 - scroll + 40 * i) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10 - scroll + 40 * i + 39):
                    pygame.draw.rect(langlist, (255, 255, 255, 127), pygame.Rect(2, 40 * i + 4, menusize[0] - 10, 34))
            try:
                langsf = colouredtext(splitcolours(languages[i]['language.name'] + ' §r(' + languages[i]['language.region'] + '§r)'), getfont('font', assets))
            except TypeError:
                langsf = colouredtext(splitcolours(languages[i]['language.name']), getfont('font', assets))
            langsfsize = list(langsf.get_rect().size)
            langsfsize[0] = langsfsize[0] * (30 / langsfsize[1])
            langsfsize[1] = 30
            langsfsize = (round(langsfsize[0]), round(langsfsize[1]))
            langsf = pygame.transform.scale(langsf, langsfsize)
            langlist.blit(langsf, (round(menusize[0] / 2 - langsfsize[0] / 2), i * 40 + 5))
            if languages[i]['language.code'] == options['language']:
                pygame.draw.rect(langlist, (255, 255, 255), pygame.Rect(2, 40 * i + 4, menusize[0] - 10, 34), 4)
            if mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10) + menusize[1]:
                if mousepos[1] >= round(windowsize[1] / 10 + titlesize[1] + 10 - scroll + 40 * i) and mousepos[1] <= round(windowsize[1] / 10 + titlesize[1] + 10 - scroll + 40 * i + 39):
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                try:
                                    getaudio('sounds.music.menu', assets).fadeout(250)
                                except AttributeError: pass
                                queue = Queue()
                                queue.end = False
                                thread = threading.Thread(target=version.scenes.reload.reload, args=[pygame, screen, clock, assets, options, lang, windowsize, pressedkeys, queue])
                                thread.setDaemon(True)
                                thread.start()
                                options['language'] = languages[i]['language.code']
                                options = setoptions(options)
                                lang, assets = loadassets(options)
                                time.sleep(1)
                                queue.end = True
                                thread.join()
                                try:
                                    windowsize, pressedkeys = queue.data
                                except AttributeError:
                                    return(True)
                                try:
                                    getasset('sounds.music.menu', assets).play(-1)
                                except AttributeError: pass
        menu.blit(langlist, (0, 0 - scroll))

        # Scroll Bar
        try:
            pygame.draw.rect(
                menu,
                (150, 150, 150),
                pygame.Rect(
                    menusize[0] - 15,
                    round(menusize[1] * (scroll / (40 * len(languages)))),
                    15,
                    round(menusize[1] / len(languages))
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

        # Menus
        display.blit(menu, (0, round(windowsize[1] / 10 + titlesize[1] + 10)))

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

        scroll += scrollvel * 5
        if scrollvel > 0:
            scrollvel -= 1
        if scrollvel < 0:
            scrollvel += 1

        if scroll < 0:
            scroll = 0
            scrollvel = 0

        if scroll > round(40 * (len(languages) - 1)):
            scroll = round(40 * (len(languages) - 1))
            scrollvel = 0

    return((assets, options, lang, windowsize, pressedkeys))