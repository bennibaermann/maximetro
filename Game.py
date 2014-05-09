# -*- coding: utf-8 -*-
from Vec2D import *
import pygame
from pygame.locals import *
import random

from config import *
from Util import *

import Station
import Passenger

class Game(object):
    """ we control from this class all the trains and lines and passengers """
    
    def __init__(self):
        self.init_game()
   

    def init_game(self):
        """ should be called at game (re)start """
        self.stations = []
        self.passengers = []
        self.LINES = list(COLORS) # avaiable lines
        self.lines = [] # existing lines
        self.init_city()
        self.score = 0


    def init_city(self):
        """we set some Stations in place."""
        
        if DEBUG: print ("Setting main station...")
        self.stations.append(Station.Station(self,(int((MAX_X-RIGHT_OFFSET)/2), int (MAX_Y/2)),\
                                "square"))
        # TODO: make sure that every shape exists
        if DEBUG: print ("Setting stations...")
        for i in range(0,MAXSTATIONS):
            pos = self.random_pos()
            if pos:
                s = Station.Station(self,pos)
                self.stations.append(s)
    

    def intersect_any(self,start,end):
        """returns True if any intersection with existing tracks"""
        for l in self.lines:
            for t in l.tracks:
                if intersect(t,start,end):
                    return True
        return False


    def build_station(self,pos):
        """builds a random station at position pos"""
        # TODO: don't build at tracks
        
        if (self.in_city_range(pos) or
            pos[0] < 2 * STATIONSIZE or
            pos[0] > MAX_X - RIGHT_OFFSET - 2 * STATIONSIZE or
            pos[1] < 2 * STATIONSIZE or
            pos[1] > MAX_Y - 2 * STATIONSIZE
            ):
            if DEBUG: print "can't build at ", pos
            return
        station = Station.Station(self,pos)
        self.stations.append(station)
        if DEBUG: print "build station at ", pos


    def in_city_range(self,pos, distance = STATIONDISTANCE):
        """returns True if pos is in distance of any station"""
        
        for s in self.stations:
            if is_in_range(pos,s.pos,distance):
                if DEBUG: print ("... is to near to ", s.pos)
                return True       
        return False
    

    def random_pos(self,distance = STATIONDISTANCE):
        """returns a random position not in range to an existing station.
        returns None if no position found after some iterations"""
        
        foundpos = False
        failed = 0
        while not foundpos and failed < 10:
            newpos = [random.randint(0 + 2 * STATIONSIZE, 
                                     MAX_X - 2 * STATIONSIZE - RIGHT_OFFSET),
                      random.randint(0 + 2 * STATIONSIZE, 
                                     MAX_Y - 2 * STATIONSIZE)]
            if DEBUG: print ("trying position ", newpos)
            foundpos = not self.in_city_range(newpos, distance)
                         
            if foundpos:
                if DEBUG: print( "position ok!")
                return newpos
            else:
                failed += 1
        return None
    

    def is_station_pos(self,pos):
        """returns center of station if at pos is a station."""
        
        for s in self.stations:
            if is_in_range(pos,s.pos):
                return s.pos
        return False
    

    def get_station(self,pos):
        """returns station at position"""
        
        return next(s for s in self.stations if s.pos == self.is_station_pos(pos))


    def update(self,counter):
        """updates (position of) all user independent objects"""
        
        for l in self.lines:
            l.update()
        for s in self.stations:
            s.update(counter)
        if FREE_PASSENGERS:
            for p in self.passengers:
                p.update()
            if random.random() < PROBABILITY_START + counter * PROBABILITY_DIFF:
                try:
                    newp = Passenger.Passenger(self)
                except Exception as e:
                    if str(e) == "nopos":
                        if DEBUG: print "found no pos, exception: ", str(e)
                    else:
                        raise e
                else:
                    self.passengers.append(newp)


    def is_track(self,start,end):
        """returns True if there is any track betwen start and end"""
    
        for l in self.lines:
            for t in l.tracks:
                if t.startpos == start and t.endpos == end:
                    return True
        return False

