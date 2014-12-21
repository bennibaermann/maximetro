# -*- coding: utf-8 -*-
from Vec2D import *
import pygame
from pygame.locals import *
import random

from config import *
from Util import *
from Semaphore import Semaphore
import Track


class Line(object):
    """A line contains multiple tracks between stations"""
    
    def __init__(self,game,start,end):
        self.game = game
        self.color = game.LINES[-1]
        self.tracks = []
        self.stations = [start,end]
        newtrack = Track.Track(self.game,start,end,self.color,self)
        
        
    def is_circle(self):
        """ returns True if line is a ring"""
        # assert len(self.tracks), "empty line"
        #print self, "anzahl tracks: ", len(self.tracks)

        # ugly workaround. this case should not apear
        #if not len(self.tracks):
        #    return False
        
        if self.tracks[0].startpos == self.tracks[-1].endpos:
            return True
        return False
        
    
    def get_cars(self):
        '''returns cars on line'''
        
        ret = []
        for t in self.tracks:
            for c in t.cars:
                ret.append(c)
        return ret

    
    def update(self):
                
        for t in self.tracks:
            if t.cars:
                for c in t.cars:
                    if c.want_move():
                        self.update_car(t,c)


    def update_car(self,track,car):
        """calculate new position of cars"""
        # global score # TODO: ugly
        
        car.pos = track.get_newpos(car.pos,car.counter,car.direction)

        if track.is_end(car.pos):
            station = self.game.get_station(car.pos)

            # which is next track?
            pil = self.tracks.index(track)
            next_pil = pil + car.direction
            if next_pil < 0 or next_pil > len(self.tracks)-1:
                if self.is_circle():
                    # this transforms from direction -1/1 to index -1/0
                    next_pil = (car.direction - 1) / 2
                else:
                    car.direction *= -1
                    next_pil = pil
                
            next_track = self.tracks[next_pil]
            
            # move car to next track
            # TODO: should be in Car-class
            track.cars.remove(car)
            next_track.add_car(car)
            car.counter = 0
            car.has_semaphore = False
            station.sem.free()
            
            # moving passengers
            platform = [] # just for intermediate memory
            copy = list(car.passengers)
            for p in copy:
                if p.leave_at(station):
                    # p leaves the car
                    car.passengers.remove(p) # TODO: PERFORMANCE
                    p.car = None
                    if p.shape == station.shape:
                        self.game.score += 1
                    else:
                        # transition
                        platform.append(p) 
            copy = list(station.passengers)
            for p in copy:
                if len(car.passengers) < CARCAPACITY and p.enter(car):
                    # p enters the car
                    station.passengers.remove(p) # TODO: PERFORMANCE
                    car.passengers.append(p)
                    p.car = car
                    p.station = None
            for p in platform:
                station.passengers.append(p)
                p.station = station
    
        car.counter += 1
        
        
    def draw(self,scr):
        for t in self.tracks:
            t.draw(scr)
            
    
    def draw_cars(self,scr):
        for t in self.tracks:
            t.draw_cars(scr)
            
            
    def __contains__(self,shape):
        """returns True if Line contains stations with shape"""

        for pos in self.stations:
            station = self.game.get_station(pos)
            if shape == station.shape:
                return True
        return False
      
        
    def delete_track(self):
        """deletes the last track from the line"""
        
        if 'track' in DEBUG: print ("delete track from line with color: ", self.color)
        track = self.tracks[-1]
        l = len(self.tracks)

        if track.cars and not l == 1:
            self.game.status = "we can't delete tracks with cars (unless last one)"
        else:
            # TODO: can we use some kind of destructor here instead?
            # delete track at stations
            starttracks = self.game.get_station(track.startpos).tracks
            endtracks =  self.game.get_station(track.endpos).tracks
            # print starttracks, endtracks
            track = self.tracks.pop()

            # if car is deleted, we handle passengers here
            if l == 1 and track.cars:
                if 'track' in DEBUG: print ("special handling of passengers in last track activated!")
                for c in track.cars:
                    offset = float(CARCAPACITY)/2 + 0.5
                    for p in c.passengers:
                        offset -= 1
                        if FREE_PASSENGERS:
                            if 'track' in DEBUG: print ("passenger leaves car.")
                            newpass = Passenger.Passenger(self.game,None,c.pos,p.shape)
                            c.shift_passenger(newpass,offset)
                            self.game.passengers.append(newpass)
                        #else: TODO without FREE_PASSENGERS they should go to next station
                        
                        if 'track' in DEBUG: print ("passenger with shape " , p.shape, " handled.")
                
            # delete semaphores for deleted cars
            for c in track.cars:
                if c.has_semaphore:
                    station = self.game.get_station(c.next_stationpos())
                    station.sem.free()

            # delete tracks at stations
            if track in starttracks:
                starttracks.remove(track)
            if track in endtracks:
                endtracks.remove(track)
                    
            if l == 1:
                self.game.LINES.append(track.color)

            del track
