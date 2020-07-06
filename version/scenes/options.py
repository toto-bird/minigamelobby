#!/usr/bin/env python

import time
from math import *
from loguru import logger
from functools import partialmethod
import sys
from pathlib import Path
import os

import version.scenes.assetpacks
import version.scenes.language

@logger.catch
def options(logger, pygame, screen, clock, assets, options, lang, windowsize, pressedkeys):
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
    def getfont(name, assets):
        try:
            return(assets[f'fonts.{name}'])
        except KeyError:
            if f'Failed To Load Font "{name}"' not in sentlogs:
                logger.error(f'Failed To Load Font "{name}"')
                sentlogs.append(f'Failed To Load Font "{name}"')
            return(pygame.font.SysFont('Comic Sans', 50))
    def getaudio(name, assets):
        try:
            return(assets[name])
        except KeyError:
            if f'Failed To Load Sound "{name}"' not in sentlogs:
                logger.error(f'Failed To Load Sound "{name}"')
                sentlogs.append(f'Failed To Load Sound "{name}"')
            return(None)
    def getlang(name, lang):
        try:
            return(lang[name])
        except KeyError:
            if f'Failed To Load Lang "{name}"' not in sentlogs:
                logger.error(f'Failed To Load Lang "{name}"')
                sentlogs.append(f'Failed To Load Lang "{name}"')
            return(name)

    logger.debug(f'Loaded Scene "options"')

    end = False
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
            elif event.type == pygame.KEYUP:
                try:
                    pressedkeys.remove(event.key)
                except KeyError: pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(6):
                        if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10) and mousepos[0] <= windowsize[0] / 2 - 10 + i % 2 * (buttonsize[0] + 10) and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * (floor(i / 2) - 1) + 10 * floor(i / 2) and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * (floor(i / 2) - 1) + 10 * floor(i / 2) + buttonsize[1]:
                            try:
                                getaudio('sounds.menu.click', assets).play()
                            except AttributeError: pass
                            if i == 2:
                                try:
                                    assets, options, lang, windowsize, pressedkeys = version.scenes.language.language(logger, pygame, screen, clock, assets, options, lang, windowsize, pressedkeys)
                                except TypeError:
                                    return(True)
                                logger.debug(f'Unloaded Scene "language"')
                            elif i == 4:
                                try:
                                    assets, options, lang, windowsize, pressedkeys = version.scenes.assetpacks.assetpacks(logger, pygame, screen, clock, assets, options, lang, windowsize, pressedkeys)
                                except TypeError:
                                    return(True)
                                logger.debug(f'Unloaded Scene "assetpacks"')
                            elif i == 8:
                                end = True
                    if mousepos[0] >= windowsize[0] / 2 - lbuttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + lbuttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 and mousepos[1] <= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 + buttonsize[1]:
                        try:
                            getaudio('sounds.menu.click', assets).play()
                        except AttributeError: pass
                        end = True

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

        lbutton = pygame.transform.scale(lbutton, lbuttonsize)

        hlbutton = getasset('textures.menu.buttons', assets)[2]
        hlbuttonsize = (round(lbuttonsize[0]), round(lbuttonsize[1]))
        hlbutton = pygame.transform.scale(hlbutton, hlbuttonsize)

        for i in range(6):
            if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10) and mousepos[0] <= windowsize[0] / 2 - 5 + i % 2 * (buttonsize[0] + 10) and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * (floor(i / 2) - 1) + 10 * floor(i / 2) and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * (floor(i / 2) - 1) + 10 * floor(i / 2) + buttonsize[1]:
                display.blit(hbutton, (windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10), windowsize[1] / 2 + buttonsize[1] * (floor(i / 2) - 1) + 10 * floor(i / 2)))
            else:
                display.blit(button, (windowsize[0] / 2 - buttonsize[0] - 5 + i % 2 * (buttonsize[0] + 10), windowsize[1] / 2 + buttonsize[1] * (floor(i / 2) - 1) + 10 * floor(i / 2)))
            l = getlang(f'optionsmenu.buttons_{i}', lang)
            if isinstance(l, str):
                buttontext = colouredtext(splitcolours(l), getfont('font', assets))
            else:
                if changed:
                    buttontext = colouredtext(splitcolours(l[1]), getfont('font', assets))
                else:
                    buttontext = colouredtext(splitcolours(l[0]), getfont('font', assets))
            buttontextsize = list(buttontext.get_rect().size)
            buttontextsize[0] = buttontextsize[0] * (buttonsize[1] / 2 / buttontextsize[1])
            buttontextsize[1] = buttonsize[1] / 2
            buttontextsize = (round(buttontextsize[0]), round(buttontextsize[1]))
            buttontext = pygame.transform.scale(buttontext, buttontextsize)

            display.blit(buttontext, (windowsize[0] / 2 - buttonsize[0] / 2 - 5 + i % 2 * (buttonsize[0] + 10) - buttontextsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * (floor(i / 2) - 1) + 10 * floor(i / 2) + buttontextsize[1] / 2))

        if mousepos[0] >= windowsize[0] / 2 - lbuttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + lbuttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 and mousepos[1] <= windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 + buttonsize[1]:
            display.blit(hlbutton, (windowsize[0] / 2 - lbuttonsize[0] / 2, windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4))
        else:
            display.blit(lbutton, (windowsize[0] / 2 - lbuttonsize[0] / 2, windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4))
        lbuttontext = colouredtext(splitcolours(getlang(f'optionsmenu.buttons_8', lang)), getfont('font', assets))
        lbuttontextsize = list(lbuttontext.get_rect().size)
        lbuttontextsize[0] = lbuttontextsize[0] * (buttonsize[1] / 2 / lbuttontextsize[1])
        lbuttontextsize[1] = lbuttonsize[1] / 2
        lbuttontextsize = (round(lbuttontextsize[0]), round(buttontextsize[1]))
        lbuttontext = pygame.transform.scale(lbuttontext, lbuttontextsize)

        display.blit(lbuttontext, (windowsize[0] / 2 - lbuttontextsize[0] / 2, windowsize[1] / 2 + lbuttonsize[1] * 1.25 * 4 + lbuttontextsize[1] / 2))

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

    return((assets, options, lang, windowsize, pressedkeys))