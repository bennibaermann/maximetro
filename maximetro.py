#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2014, Benni Baermann http://bennibaermann.de/
# COPYING: See LICENSE. This program is Free Software under AGPL

import pygame
from pygame.locals import *
import Vec2D
from Vec2D import *
import random

# own files
from Semaphore import Semaphore
from config import *
from Util import *
import Screen
import Game
import Car
import Passenger
import Track
import Line

########################################################################
# main programm
########################################################################

def main():
    # Initialise stuff
    g = Game.Game()
    status_mem = ""
    gameover = False
    count = 0
    pygame.init()
    scr = Screen.Screen(g.lines)
    screen = scr.screen
    pygame.display.set_caption('Maxi Metro')
    clock = pygame.time.Clock()

    # Event loop
    while 1:
      #try:
        count += 1
        
        # TODO: ugly code. we have to wrote some functions here
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                g.toggle_pause()      
            elif event.type == MOUSEBUTTONDOWN:
                g.status = ""
                if gameover:
                    g.init_game()
                    scr.lines = g.lines
                    count = 0
                    gameover = False
                    
                else:
                    if event.pos[0] >= MAX_X - RIGHT_OFFSET:
                        # handling of clicks at the right side (line controlling interface)
                        g.click_controlling(event)
                    else:
                        # handling of clicks at the left side (main area)
                        g.click_map(event)

            elif event.type == MOUSEMOTION and not gameover:
                if event.pos[0] >= MAX_X - RIGHT_OFFSET:
                    # we are at the right side.
                    g.mousemoving_controlling(event)
                if not CROSSING and not g.intersect_any(g.startpos,event.pos):
                    if event.pos[0] < MAX_X - RIGHT_OFFSET:
                        # we are at the left side
                        g.mousemoving_map(event)


                    
        screen.fill(WHITE)

        # draw influence aerea
        for s in g.stations:
            s.draw_aerea(scr)
        if not g.draw_status and BUILD_STATIONS:
            # draw a potential new station aerea
            try:
                # g.status = status_mem
                # status_mem = g.status
                p = event.pos
                if not g.is_station_pos(p) and g.building_place(p):
                    pygame.draw.circle(screen,VERYLIGHTGREY,p,STATIONDISTANCE)
            except:
                # TODO: better ask for the correct exception here
                if not g.pause:
                    g.status = "come back, little cursor, we need you!"
            else:
                # TODO: do not use status as flag here, bad style.
                if g.status == "come back, little cursor, we need you!":
                    g.status = ""
                
        scr.draw_interface()
        scr.status(g.status)
        scr.waiting(g.waiting)
        scr.score(g.score)

        try:
            if not gameover:
                if g.draw_status:
                    # draw a potential new track
                    if (len(g.get_station(g.startpos).get_tracks()) < MAXSTATIONTRACKS):
                        # flush_print(str(g.drawing_color))
                        pygame.draw.line(screen,g.drawing_color,g.startpos,g.pos,5)
                    else:
                        g.status = "to many tracks at station!"
                        g.draw_status = False
                        g.have_line = False
                        g.line = None
                        g.drawing_color = None
                        g.LINES.pop()
            
                if not g.pause:
                    g.update(count)
        except GameOver:
            gameover = True
            
        for l in g.lines:
            l.draw(scr)        

        # draw stations
        for s in g.stations:
            s.draw(scr)
            if 'track' in DEBUG: scr.center_text(s.pos,str(len(s.tracks)),RED)
            
        for l in g.lines:
            l.draw_cars(scr)        
            
        for p in g.passengers:
            p.draw(scr,p.pos)
    
        if gameover:
            scr.center_text((int(MAX_X/2),int(MAX_Y/2)),"GAME OVER!",BLACK,52)
            scr.center_text((int(MAX_X/2),int(MAX_Y/2)),"GAME OVER!",RED,50)
            scr.center_text((int(MAX_X/2),int(MAX_Y/2)+100),"click to restart",BLACK,20)
            g.status = "GAME OVER. click to restart."
            gameover = True
 
        pygame.display.update()
        msElapsed = clock.tick(FPS) # TODO(?): Gamespeed should be FPS-independent
    
        
if __name__ == '__main__': main()
