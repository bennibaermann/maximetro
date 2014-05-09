# -*- coding: utf-8 -*-
from Vec2D import *
import pygame
from pygame.locals import *
import random

from config import *
from Util import *
from Semaphore import Semaphore

class Station(object):
    """a station"""

    def __init__(self,game,pos,shape=''):
        self.game = game
        if not shape:
            shape = random.choice(OTHERSTATIONS)
        self.shape = shape
        self.pos = pos
        self.passengers = []
        self.sem = Semaphore()
             
        
    def draw(self,scr):
        size = 20
        pos = self.pos

        # TODO: calculate area of shapes to make it same size optical 
        #       dont use this ugly constants anymore
        innercolor = WHITE
        if DEBUG and self.sem.used:
            innercolor = BLACK
        if self.shape == 'circle':
            pygame.draw.circle(scr.screen,BLACK,pos,STATIONSIZE)
            pygame.draw.circle(scr.screen,innercolor,pos,STATIONSIZE-STATIONTHICKNESS)
        if self.shape == 'triangle':
            scr.draw_triangle(pos,STATIONSIZE+4,BLACK)
            scr.draw_triangle(pos,STATIONSIZE+4-STATIONTHICKNESS*2,innercolor)
        if self.shape == 'square':
            scr.draw_square(pos,STATIONSIZE-3,BLACK)
            scr.draw_square(pos,STATIONSIZE-STATIONTHICKNESS-3,innercolor)

        count = 0
        for p in self.passengers:
            p.draw(scr,(pos[0]+int(STATIONSIZE*1.5)+STATIONSIZE*count,pos[1]))
            count += 1
               
                
    def update(self,counter):
        
        if STATION_PASSENGERS:
            if random.random() < PROBABILITY_START + counter * PROBABILITY_DIFF:
                self.passengers.append(Passenger(self))
        
        if len(self.passengers) > MAXWAITING_STATION:
            raise GameOver("to many passengers waiting at station")
              
                
    def get_lines(self):
        """returns a list of lines connected to the station"""
        #TODO PERFORMANCE: should be stored not calculated
        
        ret = []
        for l in self.game.lines:
            for t in l.tracks:
                start = self.game.get_station(t.startpos)
                end = self.get.get_station(t.endpos)
                if start == self or end == self:
                    if l not in ret:
                        ret.append(l)
        return ret
    
    def get_tracks(self):
        """returns a list of tracks connected to the station"""
        #TODO PERFORMANCE: should be stored, not calculated
        ret = []
        for l in self.game.lines:
            for t in l.tracks:
                start = self.game.get_station(t.startpos)
                end = self.game.get_station(t.endpos)
                if start == self or end == self:
                        ret.append(t)
        return ret


    def min_distance(self,passenger,bad_tracks=[]):
        '''recursivly calculation of distance for shape of passenger. 
        bad_tracks, if any given, will be ignored'''
    
        shape = passenger.shape
        
        if DEBUG: print "min_distance(", shape,") at ", self.shape
        if self.shape == shape:
            if DEBUG: print "found", shape
            return 0

        passenger.visited.append(self)
        
        # for all tracks at station
        tracks = self.get_tracks()
        min = MAX_DEPTH
        for t in tracks:
            # ignore bad tracks
            if t in bad_tracks:
                continue
                
            # determine direction going away from next
            stationpos = t.startpos
            dir = 0
            if stationpos  == self.pos:
                dir = 1
            else:
                dir = -1
            # get distance (recursive)
            dist = t.distance(passenger,dir)
            if DEBUG: print "dist: ", dist
            if dist < min:
                min = dist
        if DEBUG: print "min: ", min
        return min
    
