# -*- coding: utf-8 -*-
from Vec2D import *
import pygame
from pygame.locals import *
import random

from config import *
from Util import *
# from Station import Station

class Passenger(object):
    """they want to travel to a station with shape self.shape!"""
    
    def __init__(self,game,station = None,pos = None, shape = None):
        self.game = game
        if station:
            self.station = station
            shapes.remove(station.shape)
        else:
            self.station = None
            
        if pos:
            self.pos = pos
        else:
            pos = self.game.random_pos(STATIONSIZE)
            if pos:
                self.pos = pos
            else:
                raise Exception("nopos")
        if shape:
            self.shape = shape
        else:
            shapes = list(SHAPES) # copy list
            self.shape = random.choice(shapes)
        
        self.car = None
        self.visited = [] # visited stations in pathfinding
        self.angle = random.randint(0,360) # random angle of movement

        
    def draw(self,scr,pos,offset=0,angle=0):

        pos = shift_pos_in_car(pos,offset,angle)
        
        if ANIMALS:
            if self.shape == 'circle':
                scr.draw_image('ladybeetle.png',pos,PASSENGERSIZE-1,BLACK,angle)
            elif self.shape == 'triangle':
                scr.draw_image('ant.png',pos,PASSENGERSIZE-1,BLACK,angle)
            elif self.shape == 'square':
                scr.draw_image('blowfish.png',pos,PASSENGERSIZE-1,BLACK,angle)
        else:
            if self.shape == 'circle':
                pygame.draw.circle(scr.screen,BLACK,pos,PASSENGERSIZE)
            elif self.shape == 'triangle':
                scr.draw_triangle(pos,PASSENGERSIZE+1,BLACK,angle)
            elif self.shape == 'square':
                scr.draw_square(pos,PASSENGERSIZE-1,BLACK,angle)
            elif self.shape == 'rhombus':
                scr.draw_rhombus(pos,PASSENGERSIZE-1,BLACK,angle)
            elif self.shape == 'semicircle':   
                scr.draw_semicircle(pos,PASSENGERSIZE-1,BLACK,angle)


    def enter(self,car,station=None):
        """returns True if this passenger wants to enter this car"""
        # assert self.game.get_station(car.pos) == self.station, "no station at enter()"
        
        if not station:
            station = self.station
        
        if 'path' in DEBUG:
            print
            print "entering enter()"
        # dont look at tracks in line of car, except
        # track with car        
        tracks_in_line = list(car.track.line.tracks)
        
        tracks_in_line.remove(car.track)
        self.visited = []
        dist = station.min_distance(self,tracks_in_line)
        if dist >= MAX_DEPTH:
            if 'path' in DEBUG: print "no path here (self)"
        next_station = self.game.get_station(car.next_stationpos())
        self.visited = []
        next_dist = next_station.min_distance(self,[car.track])
        if next_dist >= MAX_DEPTH:
            if 'path' in DEBUG: print "no path here (next)"
        if 'path' in DEBUG: print "dist: ", dist, ", next: ", next_dist
        # enter car if distance of next station is smaller
        if dist > next_dist:
            return True
        else:
            return False


    def leave_at(self,station):
        """returns True if this passenger wants to leave the car at the station"""
        # assert isinstance(station,Station), "no station in leave_at()"

        if station.shape == self.shape:
            return True
        
        if self.car:
            if not self.enter(self.car,station):
                return True
            
        return False


    def update(self):
        """moves to the next station in STATIONDISTANCE if not at station or at car"""
        assert FREE_PASSENGERS, "passenger.update() should only be called with FREEPASSENGERS = True"
            
        if self.car or self.station:
            return
        
        # find nearest station
        min_dist = 99999
        nearest = None
        for s in self.game.stations:
            d = dist(s.pos,self.pos)
            if d < min_dist:
                min_dist = d
                nearest = s
            
        if not nearest or min_dist > STATIONDISTANCE:
            self.move_random()
            return
        
        # move to nearest station
        start = Vec2d(self.pos)
        end = Vec2d(nearest.pos)
        diff = start - end
        norm = diff.normalized()
        new = start + norm * PASSENGERSPEED * -1
        self.pos = [new.x,new.y]
        
        # go to station if at station.pos
        if is_in_range(self.pos,nearest.pos):
            if 'passenger' in DEBUG: print "found station!"
            self.game.passengers.remove(self)
            if not self.shape == nearest.shape:
                self.station = nearest
                nearest.passengers.append(self)
            else:
                self.game.score += 1

   
    def move_random(self):
        '''moves randomly arround'''
        
        # TODO MAYBE: stop passengers if moving out of map?
        start = Vec2d(self.pos)
        dist = Vec2d((PASSENGERSPEED,0))
        if random.random() < PASSENGER_RANDOMNESS:
            self.angle = random.randint(0,360)
        dist.rotate(self.angle)
        new = start + dist
        self.pos = new
        
        