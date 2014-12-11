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

################################################################
# classes
################################################################

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

        
class Line(object):
    """A line contains multiple tracks between stations"""
    
    def __init__(self,game,start,end):
        self.game = game
        self.color = game.LINES[-1]
        self.tracks = []
        self.stations = [start,end]
        newtrack = Track(self.game,start,end,self.color,self)
        
        
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
                        
                        g.clean_markings()

                        # TODO: there is maybe stil a bug in CROSSING = False in seldom cases?
                        g.pos = event.pos
                        spos = g.is_station_pos(g.pos)
                        # TODO: there should be no station in the way 
                        #       (plus a little extrasize)
                        #       or: minimum angle between tracks
                        if g.draw_status and spos and not is_in_range(g.pos,g.startpos):
                            # create a potential new track
                            if (not DOUBLE_TRACKS and not g.is_track(g.startpos,spos) and
                            not g.is_track(spos,g.startpos)):
                                if (len(g.get_station(spos).get_tracks()) < MAXSTATIONTRACKS and 
                                len(g.get_station(g.startpos).get_tracks()) < MAXSTATIONTRACKS):
                                    if 'track' in DEBUG: print ("stop drawing at " , g.pos , " moving to " , spos)
                                    if g.score >= TRACKCOST:
                                        g.status = "Build track for $" + str(TRACKCOST)
                                        g.score -= TRACKCOST
                                        if g.have_line:
                                            if 'track' in DEBUG: print ("appending track to line with color", g.drawing_color)
                                            # TODO: parameter in g should not be necessary
                                            newtrack = Track(g,g.startpos,spos,g.drawing_color,g.line,0)
                                        else:
                                            if 'track' in DEBUG: print ("creating new line...")
                                            g.line = Line(g,g.startpos, spos)
                                            g.lines.append(g.line)
                                            g.have_line = True
                                        g.startpos = spos
                                    else:
                                        g.status = "Not enough money left to build track for $" + str(TRACKCOST)
                                else:
                                    g.status = "to many tracks at station!"
                            else:
                                g.status = "no doubletracks allowed!"

                    
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
                        flush_print(str(g.drawing_color))
                        pygame.draw.line(screen,g.drawing_color,g.startpos,g.pos,5)
                    else:
                        g.draw_status = False
            
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
