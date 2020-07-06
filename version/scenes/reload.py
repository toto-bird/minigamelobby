#!/usr/bin/env python

import pygame
import time
import psutil
from math import *
from pathlib import Path
import os
from loguru import logger

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

def reload(pygame, screen, clock, assets, options, lang, windowsize, pressedkeys, queue):
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
        display.set_alpha(15)

        # Background
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

        # Bars
        if round(titlesize[1] / 2 - 16) < windowsize[1] / 32:
            size = (windowsize[0] - 66, round(titlesize[1] / 2 - 16))
        else:
            size = (windowsize[0] - 66, windowsize[1] / 32)

        # CPU Bar
        pygame.draw.rect(display, (0, 0, 0), pygame.Rect(25, windowsize[1] / 2 + titlesize[1] / 2 + size[1] + 16, windowsize[0] - 50, size[1] + 16), 5)
        bar = pygame.Surface(size)
        if cpupercentage >= 0.75:
            colour = (255, 0, 0)
        elif cpupercentage >= 0.25:
            colour = (255, floor(255 - 255 * ((round(cpupercentage * 100) - 25) * 2 / 100)), 0)
        elif cpupercentage >= 0:
            colour = (floor(255 * (round(cpupercentage * 100) * 4 / 100)), 255, 0)
        else:
            colour = (0, 255, 0)
        pygame.draw.rect(bar, colour, pygame.Rect(0, 0, round(size[0] * cpupercentage), size[1]))

        cputext = colouredtext(splitcolours(getlang('loadscreen.cpuusage', lang).replace('{PERCENT}', str(round(cpupercentage * 100, 1)))), getfont('font', assets))
        cputextsize = list(cputext.get_rect().size)
        cputextsize[0] = cputextsize[0] * (size[1] / cputextsize[1])
        cputextsize[1] = size[1]
        cputextsize = (round(cputextsize[0]), round(cputextsize[1]))
        cputext = pygame.transform.scale(cputext, cputextsize)
        bar.blit(cputext, (0, 0))

        if not resize:
            screen.blit(bar, (33, windowsize[1] / 2 + titlesize[1] / 2 + size[1] + 16 + 8))

        # Memory Bar
        pygame.draw.rect(display, (0, 0, 0), pygame.Rect(25, windowsize[1] / 2 + titlesize[1] / 2 + size[1] * 3.75 + 16, windowsize[0] - 50, size[1] + 16), 5)
        bar = pygame.Surface(size)
        if rampercentage >= 0.75:
            colour = (255, 0, 0)
        elif rampercentage >= 0.25:
            colour = (255, floor(255 - 255 * ((round(rampercentage * 100) - 25) * 2 / 100)), 0)
        elif rampercentage >= 0:
            colour = (floor(255 * (round(rampercentage * 100) * 4 / 100)), 255, 0)
        else:
            colour = (0, 255, 0)
        pygame.draw.rect(bar, colour, pygame.Rect(0, 0, round(size[0] * rampercentage), size[1]))

        ramtext = colouredtext(splitcolours(getlang('loadscreen.ramusage', lang).replace('{PERCENT}', str(round(rampercentage * 100, 1)))), getfont('font', assets))
        ramtextsize = list(ramtext.get_rect().size)
        ramtextsize[0] = ramtextsize[0] * (size[1] / ramtextsize[1])
        ramtextsize[1] = size[1]
        ramtextsize = (round(ramtextsize[0]), round(ramtextsize[1]))
        ramtext = pygame.transform.scale(ramtext, ramtextsize)
        bar.blit(ramtext, (0, 0))

        if not resize:
            screen.blit(bar, (33, windowsize[1] / 2 + titlesize[1] / 2 + size[1] * 3.75 + 16 + 8))

        # Display On Screen
        if not resize:
            screen.blit(display, (0, 0))
        pygame.display.flip()
        clock.tick(120)

    queue.data = (windowsize, pressedkeys)