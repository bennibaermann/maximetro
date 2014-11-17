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
        
        if DEBUG: print "distance(",shape,",",direction,")"
        next = self.next_station(direction)
        if next in visited:
                if DEBUG: print "we where here allready"
                return MAX_DEPTH
            
        if shape == next.shape:
            if DEBUG: print "found shape ", shape
            return 1
        else:
            if DEBUG: print "not found shape ", shape, ". going recursive"
            dist = next.min_distance(passenger,[self]) # recursion
            if DEBUG: print "dist (in distance): ", dist
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
            

    def __contains__(self,shape):
        """returns True if Line contains stations with shape"""

        for pos in self.stations:
            station = self.game.get_station(pos)
            if shape == station.shape:
                return True
        return False
      
        
    def delete_track(self):
        """deletes the last track from the line"""
        
        if DEBUG: print ("delete track from line with color: ", self.color)
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
                if DEBUG: print ("special handling of passengers in last track activatet!")
                for c in track.cars:
                    for p in c.passengers:
                        if FREE_PASSENGERS:
                            if DEBUG: print ("passenger leaves car.")
                            newpass = Passenger.Passenger(self.game,None,c.pos)
                            self.game.passengers.append(newpass)
                        #else: TODO without FREE_PASSENGERS they should go to next station
                        
                        if DEBUG: print ("passenger with shape " , p.shape, " handled.")
                
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
    pause = gameover = False
    count = 0
    pygame.init()
    scr = Screen.Screen(g.lines)
    screen = scr.screen
    pygame.display.set_caption('Maxi Metro')
    clock = pygame.time.Clock()

    pos = startpos = (0,0)
    have_line = draw_status = False
    line = None
    track_to_be_deleted = None
    # Event loop
    while 1:
      #try:
        count += 1
        screen.fill(WHITE)
        scr.draw_interface()
        scr.status(g.status)
        
        # TODO: ugly code. we have to wrote some functions here
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if pause:
                    g.status = ""
                    pause = False
                else:
                    g.status = "Game paused. Press any key to resume game."
                    pause = True
                
            elif event.type == MOUSEBUTTONDOWN:
                g.status = ""
                if gameover:
                    g.init_game()
                    scr.lines = g.lines
                    pos = startpos = (0,0)
                    have_line = draw_status = False
                    line = None
                    count = 0
                    pause = gameover = False
                    
                else:
                    # handling of clicks at the right side (line controlling interface)
                    if event.pos[0] >= MAX_X - RIGHT_OFFSET:
                        color = int (event.pos[1] / 50)
                        in_use = len(COLORS) - len(g.LINES)
                        if color < in_use:
                            if event.pos[0] < MAX_X - RIGHT_OFFSET / 2:
                                line = g.lines[color]
                                line.delete_track()
                                if not line.tracks:
                                    g.lines.remove(line)
                                    # del g.lines[color]
                                track_to_be_deleted = None
                            else:
                                if DEBUG: print ("add track to line with color ", color)
                                draw_status = have_line = True
                                line = g.lines[color]
                                g.LINES.append(line.color)
                                startpos = line.tracks[-1].endpos
                    else:
                    # handling of clicks at the left side (main area)
                        pos = event.pos
                        spos = g.is_station_pos(pos)
                        if not draw_status and not spos and BUILD_STATIONS:
                            g.build_station(pos)
                        else:
                            draw_status = False
                            if have_line:
                                g.LINES.pop()
                            have_line = False
                            if g.LINES:
                                #pos = event.pos
                                #spos = is_station_pos(pos)
                                if spos and not draw_status:
                                    startpos = spos
                                    if len(g.get_station(startpos).get_tracks()) < MAXSTATIONTRACKS:
                                        if DEBUG: print ("start drawing from " ,pos, " moving to ", startpos)
                                        draw_status = True

                                    else:
                                        g.status = "no more tracks avaiable at this station"
                            else:
                                g.status = "NO MORE LINES AVAIABLE!"
                            
                                
            elif event.type == MOUSEMOTION and not gameover:
                if not CROSSING and not g.intersect_any(startpos,event.pos):

                    # we are at the right side.
                    if event.pos[0] >= MAX_X - RIGHT_OFFSET:
                        color = int (event.pos[1] / 50)
                        in_use = len(COLORS) - len(g.LINES)
                        if color < in_use:
                            if event.pos[0] < MAX_X - RIGHT_OFFSET / 2:
                                line = g.lines[color]
                                if track_to_be_deleted:
                                    track_to_be_deleted.to_be_deleted = False
                                track_to_be_deleted = line.tracks[-1]
                                track_to_be_deleted.to_be_deleted = True
                            
                            else:
                                if track_to_be_deleted:
                                    track_to_be_deleted.to_be_deleted = False

#                                if DEBUG: print ("add track to line with color ", color)
#                                draw_status = have_line = True
#                                line = g.lines[color]
#                                g.LINES.append(line.color)
#                                startpos = line.tracks[-1].endpos                    
                    
                    else:
                        if track_to_be_deleted:
                            track_to_be_deleted.to_be_deleted = False

                        
                    
                    # TODO: there is stil a bug in CROSSING = False in seldom cases
                    pos = event.pos
                    spos = g.is_station_pos(pos)
                    # TODO: there should be no station in the way 
                    #       (plus a little extrasize)
                    #       or: minimum angle between tracks
                    if draw_status and spos and not is_in_range(pos,startpos):
                        if (not DOUBLE_TRACKS and not g.is_track(startpos,spos) and
                           not g.is_track(spos,startpos)):
                            if (len(g.get_station(spos).get_tracks()) < MAXSTATIONTRACKS and 
                                len(g.get_station(startpos).get_tracks()) < MAXSTATIONTRACKS):
                                if DEBUG: print ("stop drawing at " , pos , " moving to " , spos)
                                if have_line:
                                    if DEBUG: print ("appending track to line...")
                                    # startpos = spos
                                    newtrack = Track(g,startpos,spos,line.color,line,0)
                                else:
                                    if DEBUG: print ("creating new line...")
                                    line = Line(g,startpos, spos)
                                    g.lines.append(line)
                                    have_line = True
                                startpos = spos
                            else:
                                g.status = "to many tracks at station!"
                        else:
                            g.status = "no doubletracks allowed!"
                            

        if pause and not gameover:
            scr.pause()
        scr.waiting(g.waiting)
        scr.score(g.score)
        
        try:
            if not gameover:
                if draw_status:
                    if (len(g.get_station(startpos).get_tracks()) < MAXSTATIONTRACKS):
                        pygame.draw.line(screen,g.LINES[-1],startpos,pos,5)
                    else:
                        draw_status = False
                if not pause:
                    g.update(count)
        except GameOver:
            gameover = True
            
        for l in g.lines:
            l.draw(scr)        
            
        for s in g.stations:
            s.draw(scr)
            if DEBUG: scr.center_text(s.pos,str(len(s.tracks)),RED)
            
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
