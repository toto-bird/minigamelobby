#!/usr/bin/env python

import time
from loguru import logger

logger.catch()
def broken(logger, pygame, screen, clock, assets, options, lang, windowsize):
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

    def wrappedtext(text, font, maxwidth):
        cur = [[]]
        width = 0
        height = 0
        totalwidth = 0
        totalheight = 0
        i = text.split(' ')
        text = []
        for j in i:
            text.append(j)
            text.append(' ')
        text = text[:-1]
        for i in text:
            r = font.render(i, False, (255, 85, 85))
            rsize = r.get_rect().size
            if len(cur[-1]) <= 0 and rsize[1] >= height:
                height = rsize[1]
            if width + rsize[0] * 2 > maxwidth * 0.77:
                if len(cur[-1]) <= 0:
                    cur[-1].append((r, rsize))
                    if width > totalwidth:
                        totalwidth = width
                    cur.append([])
                else:
                    if width > totalwidth:
                        totalwidth = width
                    cur.append([(r, rsize)])
                width = 0
            else:
                cur[-1].append((r, rsize))
                width += rsize[0]
        ret = pygame.Surface((maxwidth * 2, height * len(cur) * 2), pygame.SRCALPHA)
        retheight = 0
        for i in cur:
            linewidth = 0
            for j in i:
                linewidth += j[1][0]
            line = pygame.Surface((linewidth, height), pygame.SRCALPHA)
            linewidth = 0
            for j in i:
                line.blit(j[0], (linewidth, 0))
                linewidth += j[1][0]
            ret.blit(line, (round(maxwidth - linewidth / 2), retheight + 25))
            retheight += height
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

    logger.debug(f'Loaded Scene "broken"')

    logger.fatal('This Version Of The Game Is Broken And Has Been Removed. Please Switch To A Different Version Of The Game.')

    while True:
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
                print('End')
                return(True)
            elif event.type == pygame.VIDEORESIZE:
                windowsize = (event.w, event.h)
                screen = pygame.display.set_mode(windowsize, pygame.RESIZABLE|pygame.DOUBLEBUF)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + buttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * 5 and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * 5 + buttonsize[1]:
                        try:
                            getasset('sounds.menu.click', assets).play()
                        except AttributeError: pass
                        return(True)

        # Clear Screen
        display = pygame.Surface(windowsize)
        display.set_alpha(50)
        display.fill((0, 0, 0))

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

        # Error Message
        message = wrappedtext(getlang('broken.message', lang), getfont('debug', assets), windowsize[0])
        messagesize = list(message.get_rect().size)
        messagesize[0] = messagesize[0] * (windowsize[1] / 1.5 / messagesize[1])
        messagesize[1] = windowsize[1] / 1.5
        if messagesize[0] > windowsize[0] * 1.8:
            messagesize[1] = messagesize[1] * (windowsize[0] * 1.8 / messagesize[0])
            messagesize[0] = windowsize[0] * 1.8
        messagesize = (round(messagesize[0]), round(messagesize[1]))
        message = pygame.transform.scale(message, messagesize)
        display.blit(message, (windowsize[0] / 2 - messagesize[0] / 2, windowsize[1] * 2 / 3 - messagesize[1] / 2))

        # Buttons
        button = pygame.transform.scale(button, buttonsize)

        hbutton = getasset('textures.menu.buttons', assets)[2]
        hbuttonsize = (round(buttonsize[0]), round(buttonsize[1]))
        hbutton = pygame.transform.scale(hbutton, hbuttonsize)

        for i in range(1):
            if mousepos[0] >= windowsize[0] / 2 - buttonsize[0] / 2 and mousepos[0] <= windowsize[0] / 2 + buttonsize[0] / 2 and mousepos[1] >= windowsize[1] / 2 + buttonsize[1] * (i + 5) and mousepos[1] <= windowsize[1] / 2 + buttonsize[1] * (i + 5) + buttonsize[1]:
                display.blit(hbutton, (windowsize[0] / 2 - buttonsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * (i + 5)))
            else:
                display.blit(button, (windowsize[0] / 2 - buttonsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * (i + 5)))
            buttontext = colouredtext(splitcolours(getlang(f'broken.buttons_{i}', lang)), getfont('font', assets))
            buttontextsize = list(buttontext.get_rect().size)
            buttontextsize[0] = buttontextsize[0] * (buttonsize[1] / 2 / buttontextsize[1])
            buttontextsize[1] = buttonsize[1] / 2
            buttontextsize = (round(buttontextsize[0]), round(buttontextsize[1]))
            buttontext = pygame.transform.scale(buttontext, buttontextsize)

            display.blit(buttontext, (windowsize[0] / 2 - buttontextsize[0] / 2, windowsize[1] / 2 + buttonsize[1] * 1.25 * (i + 4) + buttontextsize[1] / 2))

        # Display On Screen
        screen.blit(display, (0, 0))
        pygame.display.flip()
        clock.tick(120)