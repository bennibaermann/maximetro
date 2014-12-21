# -*- coding: utf-8 -*-
from Vec2D import *
import pygame
from pygame.locals import *
import random

from config import *
from Util import *
from Semaphore import Semaphore
import Car


class Track(object):
    """A railtrack between stations."""
    
    def __init__(self,game,start,end,color,line,withcar=True):
        """constructor should only be called, if LINES[] is not empty"""
        assert game.LINES, "no more lines available"

        self.game = game
        self.line = line
        self.color = color
        self.startpos = start
        self.endpos = end
        self.cars = []
        if withcar:
            self.cars.append(Car.Car(self.game,self))

        # lines ans stations connected with us should know of our existence
        self.line.tracks.append(self)
        self.line.stations.append(end) # TODO: should not be double if circle
        self.game.get_station(start).tracks.append(self)
        self.game.get_station(end).tracks.append(self)            
        
        self.to_be_deleted = False
        
    def draw(self,scr):
        if self.to_be_deleted:
            pygame.draw.line(scr.screen,BLACK,self.startpos,self.endpos,5)
        else:
            pygame.draw.line(scr.screen,self.color,self.startpos,self.endpos,5)
        

    def draw_cars(self,scr):
        for c in self.cars:
            c.draw(scr)
          

    def length(self):
        """returns the length of the track"""
        
        #TODO PERFORMANCE: calculate only once if track changes
        return dist(self.startpos,self.endpos)
        
    def get_newpos(self,pos,count,direction=1,i=1):
        """ calculates new position of a car in i iterations"""
    
        count += (i - 1)
        start = self.startpos
        end = self.endpos
        ret = [0,0]
        length = self.length()
        xdiff = (start[0] - end[0]) / length * CARSPEED * -1
        ydiff = (start[1] - end[1]) / length * CARSPEED * -1
        if direction > 0:
            ret[0] = int(xdiff * count) + start[0]
            ret[1] = int(ydiff * count) + start[1]
        else:
            ret[0] = end[0] - int(xdiff * count)
            ret[1] = end[1] - int(ydiff * count)
        return ret
     
        
    def is_end(self,pos):
        """returns True if pos is not on track"""
    
        start = self.startpos
        end = self.endpos
        x_range = [start[0],end[0]]
        y_range = [start[1],end[1]]
        x_range.sort()
        y_range.sort()
        if (x_range[0] <= pos[0] <= x_range[1] and 
           y_range[0] <= pos[1] <= y_range[1]):
            return False
        return True
    
    
    def add_car(self,car):
        car.track = self
        self.cars.append(car)
    
    def next_station(self,direction):
        """returns the station at this track in direction"""
        
        if direction > 0:
            return self.game.get_station(self.endpos)
        elif direction < 0:
            return self.game.get_station(self.startpos)
        else:
            assert 0, "impossible direction: 0"
            

    def distance(self,passenger,direction):
        """calculates recursivly the distance (in tracks) to the
        nearest station with shape in direction"""
        
        # special handling of circles. return MAX_DEPTH
        # if wrong direction and only one car at line
        # TODO: what if more than one car but all same direction?
        if self.line.is_circle():
            cars = self.line.get_cars()
            if len(cars) == 1:
                if cars[0].direction != direction:
                    return MAX_DEPTH                
                
        shape = passenger.shape
        visited = passenger.visited
        
        if 'path' in DEBUG: print "distance(",shape,",",direction,")"
        next = self.next_station(direction)
        if next in visited:
                if 'path' in DEBUG: print "we where here allready"
                return MAX_DEPTH
            
        if shape == next.shape:
            if 'path' in DEBUG: print "found shape ", shape
            return 1
        else:
            if 'path' in DEBUG: print "not found shape ", shape, ". going recursive"
            dist = next.min_distance(passenger,[self]) # recursion
            if 'path' in DEBUG: print "dist (in distance): ", dist
            return dist + 1
