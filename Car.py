# -*- coding: utf-8 -*-
from Vec2D import *
import pygame
from pygame.locals import *
import random

from config import *
from Util import *
from Semaphore import Semaphore

class Car(object):
    """A railcar. Each Line holds at least one"""
    
    def __init__(self,game,track):
        self.game = game
        self.track = track
        self.pos = track.startpos
        self.direction = 1
        self.counter = 0
        self.poly = ((-CARWITH,-CARLENGTH),(-CARWITH,CARLENGTH),
                     (CARWITH,CARLENGTH),(CARWITH,-CARLENGTH))
        self.passengers = []
        self.angle = 0
        self.has_semaphore = False
            
            
    def move(self):
        """returns the moved polygon to self.pos with angle of self.track"""

        ret = []
        pol = self.poly

        # determine angle of track 
        # TODO PERFORMANCE: should be calculated only once
        start = self.track.startpos
        end = self.track.endpos
        v = Vec2d(start[0]-end[0],start[1]-end[1])
        self.angle = v.get_angle() + 90
        
        # rotate car
        turnedpol = rotate_poly(pol,self.angle)
    
        # move to self.pos
        ret = move_poly(turnedpol,self.pos)
        
        return ret
        
            
    def car_in_range(self, alternative_position=None):
        """returns a list with cars in range CARLENGTH * 3 from pos"""
        
        ret = []
        for l in self.game.lines:
            for t in l.tracks:
                for c in t.cars:
                    if c != self:
                        if alternative_position:
                            # we test not with the position of the car, but with another
                            if(is_in_range(c.pos,alternative_position,CARLENGTH*3)):
                                ret.append(c)
                        else:
                            if is_in_range(c.pos,self.pos,CARLENGTH*3):
                                ret.append(c)
            
        return ret

    def next_stationpos(self):
        """returns the next target of the car"""
        
        if self.direction > 0:
            return self.track.endpos
        elif self.direction < 0:
            return self.track.startpos
        else:
            assert 0, "impossible direction: 0"
            
        
    def last_stationpos(self):
        """returns the last origin of the car"""
    
        if self.direction < 0:
            return self.track.endpos
        elif self.direction > 0:
            return self.track.startpos
        else:
            assert 0, "impossible direction: 0"
            
        
    def want_move(self):
        """collision detection is handled here"""
        
        if COLLISION == True:
            # there is no moving restriction if collision-detection is off
            return True
        else:
            #calculate distance from start
            start = self.last_stationpos()
            end = self.next_stationpos()
            dist = ( (start[0]-self.pos[0])**2 + (start[1]-self.pos[1])**2 ) ** .5
            # stay at center of track unless we have a free station
            if dist < self.track.length() / 2:
                return True
            else:
                sema = self.game.get_station(end).sem
                if sema.used and not self.has_semaphore:
                    return False
                elif not self.has_semaphore:                    
                    sema.block(self)
                    self.has_semaphore = True
                    return True
                else:
                    return True
 
   
    def draw(self,scr):
        """draw the car."""

        moved = self.move()
        #if self.waiting and DEBUG:
        #    pygame.draw.polygon(screen,BLACK,moved,0)
        #else:
        pygame.draw.polygon(scr.screen,self.track.color,moved,0)
        # if DEBUG:
            #future_pos = self.track.get_newpos(self.pos,self.counter,self.direction,CARLENGTH/CARSPEED * 3)
            #pygame.draw.circle(screen,self.track.color,future_pos,CARLENGTH*3,2)
            #if self in semaphore:
            #    pygame.draw.circle(screen,WHITE,self.pos,10)
            #
        # drawing of passengers
        # TODO: stil buggy for some values of CARCAPACITY
        offset = CARCAPACITY/2 + 1
        for p in self.passengers:
            offset -= 1
            p.draw(scr,self.pos,offset,self.angle)

