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
        self.pause = False
        self.stations = []
        self.passengers = []
        self.waiting = 0
        self.LINES = list(COLORS) # avaiable lines
        self.lines = [] # existing lines
        self.init_city()
        self.score = STARTMONEY
        self.status = "Help passengers find theire home! Click to build stations. Click at stations to build tracks."
        self.line = None # the line, which is actual handled in the interface
        self.track_to_be_deleted = None
        self.pos = (0,0) # last position of action
        self.startpos = (0,0) # start position of actual handled track
        self.draw_status = False
        self.have_line = False
        
    def init_city(self):
        """we set some Stations in place."""
        
        if 'init' in DEBUG: print ("Setting main station...")
        self.stations.append(Station.Station(self,(int((MAX_X-RIGHT_OFFSET)/2), int (MAX_Y/2)),\
                                "square"))
        # TODO: make sure that every shape exists
        if 'init' in DEBUG: print ("Setting stations...")
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

    
    def building_place(self,pos):
        """checks if we can build a station at pos"""
        
        # TODO: don't build at tracks
        if (self.in_city_range(pos) or
            pos[0] < 2 * STATIONSIZE or
            pos[0] > MAX_X - RIGHT_OFFSET - 2 * STATIONSIZE or
            pos[1] < 2 * STATIONSIZE or
            pos[1] > MAX_Y - 2 * STATIONSIZE
            ):
                return False
        return True
        
    
    def build_station(self,pos):
        """builds a random station at position pos"""

        if not self.building_place(pos):
            if 'station' in DEBUG: print "can't build at ", pos
            self.status = "No place for station here."
            return
        if self.score >= STATIONCOST:
            station = Station.Station(self,pos)
            self.stations.append(station)
            if 'station' in DEBUG: print "build station at ", pos
            self.status = "build station for $" + str(STATIONCOST)
            self.score -= STATIONCOST
        else:
            self.status = "Not enough money left to build station. You need $" + str(STATIONCOST)
            
            
    def in_city_range(self,pos, distance = STATIONDISTANCE):
        """returns True if pos is in distance of any station"""
        
        for s in self.stations:
            if is_in_range(pos,s.pos,distance):
                if 'station' in DEBUG: print ("... is to near to ", s.pos)
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
            if 'random' in DEBUG: print ("trying position ", newpos)
            foundpos = not self.in_city_range(newpos, distance)
                         
            if foundpos:
                if 'random' in DEBUG: print( "position ok!")
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
        
        self.waiting = 0
        for l in self.lines:
            l.update()
        for s in self.stations:
            s.update(counter)
            self.waiting += len(s.passengers)
        if FREE_PASSENGERS:
            for p in self.passengers:
                p.update()
            if random.random() < PROBABILITY_START + counter * PROBABILITY_DIFF:
                try:
                    newp = Passenger.Passenger(self)
                except Exception as e:
                    if str(e) == "nopos":
                        if 'passenger' in DEBUG: print "found no pos, exception: ", str(e)
                    else:
                        raise e
                else:
                    self.passengers.append(newp)

        self.waiting += len(self.passengers)
        if self.waiting > MAXWAITING:
            raise GameOver("to many passengers waiting")
        
        
    def is_track(self,start,end):
        """returns True if there is any track betwen start and end"""
    
        for l in self.lines:
            for t in l.tracks:
                if t.startpos == start and t.endpos == end:
                    return True
        return False

    
    def toggle_pause(self):
        '''toggle pause-status of the game'''
            
        if self.pause:
            self.status = ""
            self.pause = False
        else:
            self.status = "Game paused. Press any key to resume game."
            self.pause = True
                                                
                    
    def click_controlling(self,event):
        """ handling of clicks at the right side (line controlling interface)"""
        
        if event.pos[0] >= MAX_X - RIGHT_OFFSET:
            color = int (event.pos[1] / 50)
            in_use = len(COLORS) - len(self.LINES)
            if color < in_use:
                if event.pos[0] < MAX_X - RIGHT_OFFSET / 2:
                    if self.score >= DELETECOST:
                        self.status = "Delete Track for $" + str(DELETECOST)
                        self.score -= DELETECOST
                        self.line = self.lines[color]
                        self.line.delete_track()
                        if not self.line.tracks:
                            self.lines.remove(self.line)
                        self.track_to_be_deleted = None
                    else:
                        self.status = "Not enough money left to delete track for $" + str(DELETECOST)
                else:
                    if 'track' in DEBUG: print ("add track to line with color ", color)
                    self.draw_status = self.have_line = True
                    self.line = self.lines[color]
                    self.LINES.append(self.line.color)
                    self.startpos = self.line.tracks[-1].endpos
        
                    
    def click_map(self,event):
        ''' handling of clicks at the map at left side (main area)'''
        
        self.pos = event.pos
        spos = self.is_station_pos(self.pos)
        if not self.draw_status and not spos and BUILD_STATIONS:
            self.build_station(self.pos)
        else:
            self.draw_status = False
            if self.have_line:
                self.LINES.pop()
            self.have_line = False
            if self.LINES:
                if spos and not self.draw_status:
                    self.startpos = spos
                    if len(self.get_station(self.startpos).get_tracks()) < MAXSTATIONTRACKS:
                        if 'track' in DEBUG: print ("start drawing from " , self.pos, " moving to ", self.startpos)
                        self.draw_status = True
                        
                    else:
                        self.status = "no more tracks avaiable at this station"
                else:
                    self.status = "NO MORE LINES AVAIABLE!"
                    
                    
    def mousemoving_controlling(self,event):
        '''handle mouse change coordinates in the controler-interface at the right side'''
        
        color = int (event.pos[1] / 50)
        in_use = len(COLORS) - len(self.LINES)
        if color < in_use:
            if event.pos[0] < MAX_X - RIGHT_OFFSET / 2:
                self.line = self.lines[color]
                if self.track_to_be_deleted:
                    self.track_to_be_deleted.to_be_deleted = False
                self.track_to_be_deleted = self.line.tracks[-1]
                self.track_to_be_deleted.to_be_deleted = True
                return
        if self.track_to_be_deleted:
            self.track_to_be_deleted.to_be_deleted = False
                    
