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

################################################################
# global variables
################################################################

score = 0
stations = []
lines = []
passengers = [] # only free passengers, which are not in a car or at a station

################################################################
# global functions
################################################################

# use global (lines)
def intersect_any(start,end):
    """returns True if any intersection with existing tracks"""
    for l in lines:
        for t in l.tracks:
            if intersect(t,start,end):
                return True
    return False


#use globals (all)
def init_game():
    """ should be called at game (re)start """
    global lines, stations, LINES, score, passengers
    stations = []
    lines = []
    passengers = []
    LINES = list(COLORS)
    init_city()
    score = 0
   
# use Station, use global (stations)
def build_station(pos):
    """builds a random station at position pos"""
    # TODO: don't build at tracks
    
    if (in_city_range(pos) or
        pos[0] < 2 * STATIONSIZE or
        pos[0] > MAX_X - RIGHT_OFFSET - 2 * STATIONSIZE or
        pos[1] < 2 * STATIONSIZE or
        pos[1] > MAX_Y - 2 * STATIONSIZE
        ):
        print "can't build at ", pos
        return
    station = Station(pos)
    stations.append(station)
    print "build station at ", pos
    

#use global (stations)
def in_city_range(pos, distance = STATIONDISTANCE):
    """returns True if pos is in distance of any station"""
    
    for s in stations:
        if is_in_range(pos,s.pos,distance):
            if DEBUG: print ("... is to near to ", s.pos)
            return True       
    return False

# use global (stations via in_city_range)
def random_pos(distance = STATIONDISTANCE):
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
        foundpos = not in_city_range(newpos)
        #for s in stations:
        #    if is_in_range(newpos,s.pos,distance):
        #        foundpos = False
        #        if DEBUG: print ("... is to near to ", s.pos)
                    
        if foundpos:
            if DEBUG: print( "position ok!")
            return newpos
        else:
            failed += 1
    return None

# use Station, use global (stations)
def init_city():
    """we set some Stations in place."""
    
    print ("Setting main station...")
    stations.append(Station((int((MAX_X-RIGHT_OFFSET)/2), int (MAX_Y/2)),\
                            "square"))
    # TODO: make sure that every shape exists
    print ("Setting stations...")
    for i in range(0,MAXSTATIONS):
        pos = random_pos()
        if pos:
            s = Station(pos)
            stations.append(s)


        
# use global (stations)
def is_station_pos(pos):
    """returns center of station if at pos is a station."""
    
    for s in stations:
        if is_in_range(pos,s.pos):
            return s.pos
    return False

# use global (stations)
def get_station(pos):
    """returns station at position"""
    
    return next(s for s in stations if s.pos == is_station_pos(pos))

# use global (lines,stations,passengers) use Passenger
def update(counter):
    """updates (position of) all user independent objects"""
    
    for l in lines:
        l.update()
    for s in stations:
        s.update(counter)
    if FREE_PASSENGERS:
        for p in passengers:
            p.update()
        if random.random() < PROBABILITY_START + counter * PROBABILITY_DIFF:
            try:
                newp = Passenger()
            except Exception as e:
                if str(e) == "nopos":
                    if DEBUG: print "found no pos, exception: ", str(e)
                else:
                    raise e
            else:
                passengers.append(newp)
            
# use global (lines)
def is_track(start,end):
    """returns True if there is any track betwen start and end"""

    for l in lines:
        for t in l.tracks:
            if t.startpos == start and t.endpos == end:
                return True
    return False

    

################################################################
# classes
################################################################

# exceptions
class GameOver(Exception): pass

class Car(object):
    """A railcar. Each Line holds at least one"""
    
    def __init__(self,track):
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
        for l in lines:
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
                sema = get_station(end).sem
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



class Track(object):
    """A railtrack between stations."""
    
    def __init__(self,start,end,color,line,withcar=True):
        """constructor should only be called, if LINES[] is not empty"""
        assert LINES, "no more lines available"

        self.line = line
        self.color = color
        self.startpos = start
        self.endpos = end
        self.cars = []
        if withcar:
            self.cars.append(Car(self))
            
        
    def draw(self,scr):
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
            return get_station(self.endpos)
        elif direction < 0:
            return get_station(self.startpos)
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
            # return minimal distance + 1
            #if dist >= MAX_DEPTH:
            return dist + 1

        
class Line(object):
    """A line contains multiple tracks between stations"""
    
    def __init__(self,start,end):
        self.color = LINES[-1]
        self.tracks = []
        self.tracks.append(Track(start,end,self.color,self))
        self.stations = [start,end]
        
        
    def is_circle(self):
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
        global score # TODO: ugly
        
        car.pos = track.get_newpos(car.pos,car.counter,car.direction)

        if track.is_end(car.pos):
            station = get_station(car.pos)

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
                        score += 1
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
            station = get_station(pos)
            if shape == station.shape:
                return True
        return False
      
        
    def delete_track(self):
        """deletes the last track from the line"""
        
        if DEBUG: print ("delete track from line with color: ", self.color)
        track = self.tracks[-1]
        l = len(self.tracks)
        if track.cars and not l == 1:
            print ("we can't delete tracks with cars (unless last one)")
        else:
            # TODO: if car is deleted, we should do something
            #       with the passengers...
            track = self.tracks.pop()
            # delete semaphores for deleted cars
            # TODO: can we use some kind of destructor here instead?
            for c in track.cars:
                if c.has_semaphore:
                    station = get_station(c.next_stationpos())
                    station.sem.free()
                    
            if l == 1:
                LINES.append(track.color)
        
        

class Passenger(object):
    """they want to travel to a station with shape self.shape!"""
    
    def __init__(self,station = None):
        if station:
            self.station = station
            shapes.remove(station.shape)
        else:
            pos = random_pos(STATIONSIZE)
            if pos:
                self.pos = pos
            else:
                raise Exception("nopos")
            self.station = None
        shapes = list(SHAPES) # copy list
        self.shape = random.choice(shapes)
        self.car = None
        self.visited = [] # visited stations in pathfinding

        
    def draw(self,scr,pos,offset=0,angle=0):
        # generate vector in angle and length PASSENGERSIZE
        v = Vec2d(PASSENGERSIZE*3,0)
        v.rotate(angle+90)
        
        # add vector for every offset to pos
        v_pos = Vec2d(pos)
        v_new = v_pos + v * offset
        pos = (int(v_new.x),int(v_new.y))
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
            

    def enter(self,car,station=None):
        """returns True if this passenger wants to enter this car"""
        assert get_station(car.pos) == self.station or isinstance(station,Station), "no station at enter()"
        
        if not station:
            station = self.station
        
        if DEBUG:
            print
            print "entering enter()"
        # dont look at tracks in line of car, except
        # track with car        
        tracks_in_line = list(car.track.line.tracks)
        
        tracks_in_line.remove(car.track)
        self.visited = []
        dist = station.min_distance(self,tracks_in_line)
        if dist >= MAX_DEPTH:
            if DEBUG: print "no path here (self)"
        next_station = get_station(car.next_stationpos())
        self.visited = []
        next_dist = next_station.min_distance(self,[car.track])
        if next_dist >= MAX_DEPTH:
            if DEBUG: print "no path here (next)"
        if DEBUG: print "dist: ", dist, ", next: ", next_dist
        # enter car if distance of next station is smaller
        if dist > next_dist:
            return True
        else:
            return False
        
        
    def leave_at(self,station):
        """returns True if this passenger wants to leave the car at the station"""
        assert isinstance(station,Station), "no station in leave_at()"

        if station.shape == self.shape:
            return True
        
        if self.car:
            if not self.enter(self.car,station):
                return True
            
        return False


    def update(self):
        """moves to the next station in STATIONDISTANCE if not at station or at car"""
        assert FREE_PASSENGERS, "passenger.update() should only be called with FREEPASSENGERS = True"
        global score
        
        if self.car or self.station:
            return
        
        # find nearest station
        min_dist = 99999
        nearest = None
        for s in stations:
            d = dist(s.pos,self.pos)
            if d < min_dist:
                min_dist = d
                nearest = s
            
        if not nearest:
            return

        # print "found nearest station at: ", nearest.pos
        
        if min_dist > STATIONDISTANCE:
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
            if DEBUG: print "found station!"
            passengers.remove(self)
            if not self.shape == nearest.shape:
                self.station = nearest
                nearest.passengers.append(self)
            else:
                score += 1
                
                
class Station(object):
    """a station"""

    def __init__(self,pos,shape=''):
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
        
        if len(self.passengers) > MAXWAITING:
            raise GameOver("to many passengers waiting")
              
                
    def get_lines(self):
        """returns a list of lines connected to the station"""
        #TODO PERFORMANCE: should be stored not calculated
        
        ret = []
        for l in lines:
            for t in l.tracks:
                start = get_station(t.startpos)
                end = get_station(t.endpos)
                if start == self or end == self:
                    if l not in ret:
                        ret.append(l)
        return ret
    
    def get_tracks(self):
        """returns a list of tracks connected to the station"""
        #TODO PERFORMANCE: should be stored, not calculated
        ret = []
        for l in lines:
            for t in l.tracks:
                start = get_station(t.startpos)
                end = get_station(t.endpos)
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
    

########################################################################
# main programm
########################################################################
                        
def main():
    # Initialise stuff
    init_game()
    pause = gameover = False
    count = 0
    pygame.init()
    scr = Screen.Screen(lines)
    screen = scr.screen
    pygame.display.set_caption('Maxi Metro')
    clock = pygame.time.Clock()
    
    pos = startpos = (0,0)
    have_line = draw_status = False
    line = None
    # Event loop
    while 1:
      #try:
        count += 1
            
        # TODO: ugly code. we have to wrote some functions here
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if pause:
                    pause = False
                else:
                    pause = True
                
            elif event.type == MOUSEBUTTONDOWN:
                if gameover:
                    init_game()
                    pos = startpos = (0,0)
                    have_line = draw_status = False
                    line = None
                    count = 0
                    pause = gameover = False
                    
                else:
                    # handling of clicks at the right side
                    if event.pos[0] >= MAX_X - RIGHT_OFFSET:
                        color = int (event.pos[1] / 50)
                        in_use = len(COLORS) - len(LINES)
                        if color < in_use:
                            if event.pos[0] < MAX_X - RIGHT_OFFSET / 2:
                                line = lines[color]
                                line.delete_track()
                                if not line.tracks:
                                    del lines[color]
                            else:
                                if DEBUG: print ("add track to line with color ", color)
                                draw_status = have_line = True
                                line = lines[color]
                                LINES.append(line.color)
                                startpos = line.tracks[-1].endpos
                    else:
                        pos = event.pos
                        spos = is_station_pos(pos)
                        if not draw_status and not spos and BUILD_STATIONS:
                            build_station(pos)
                        else:
                            draw_status = False
                            if have_line:
                                LINES.pop()
                            have_line = False
                            if LINES:
                                #pos = event.pos
                                #spos = is_station_pos(pos)
                                if spos and not draw_status:
                                    startpos = spos
                                    if len(get_station(startpos).get_tracks()) < MAXSTATIONTRACKS:
                                        if DEBUG: print ("start drawing from " ,pos, " moving to ", startpos)
                                        draw_status = True
                                    else:
                                        print("no more tracks avaiable at this station")
                            else:
                                print ("NO MORE LINES AVAIABLE!")
                            
                                
            elif event.type == MOUSEMOTION and not gameover:
                if not CROSSING and not intersect_any(startpos,event.pos):
                    # TODO: there is stil a bug in CROSSING = False in seldom cases
                    pos = event.pos
                    spos = is_station_pos(pos)
                    # TODO: there should be no station in the way 
                    #       (plus a little extrasize)
                    #       or: minimum angle between tracks
                    if draw_status and spos and not is_in_range(pos,startpos):
                        if (not DOUBLE_TRACKS and not is_track(startpos,spos) and
                           not is_track(spos,startpos)):
                            if (MAXSTATIONTRACKS and
                                len(get_station(spos).get_tracks()) < MAXSTATIONTRACKS and 
                                len(get_station(startpos).get_tracks()) < MAXSTATIONTRACKS):
                                if DEBUG: print ("stop drawing at " , pos , " moving to " , spos)
                                if have_line:
                                    if DEBUG: print ("appending track to line...")
                                    # startpos = spos
            
                                    line.tracks.append(Track(startpos,spos,line.color,line,0))
                                    line.stations.append(spos) # TODO: should not be double if circle
                                else:
                                    if DEBUG: print ("creating new line...")
                                    line = Line(startpos, spos)
                                    lines.append(line)
                                    have_line = True
                                startpos = spos
                            else:
                                print("to many tracks at station!")
                        else:
                            print("no doubletracks allowed!")
                            
        screen.fill(WHITE)
        scr.draw_interface()
        if pause and not gameover:
            scr.pause()
        scr.score(score)
        
        try:
            if not gameover:
                if draw_status:
                    if (MAXSTATIONTRACKS and len(get_station(startpos).get_tracks()) < MAXSTATIONTRACKS):
                        pygame.draw.line(screen,LINES[-1],startpos,pos,5)
                    else:
                        draw_status = False
                if not pause:
                    update(count)
        except GameOver:
            gameover = True
            
        for l in lines:
            l.draw(scr)        
            
        for s in stations:
            s.draw(scr)
            
        for p in passengers:
            p.draw(scr,p.pos)
    
        if gameover:
            scr.center_text((int(MAX_X/2),int(MAX_Y/2)),"GAME OVER!",BLACK,52)
            scr.center_text((int(MAX_X/2),int(MAX_Y/2)),"GAME OVER!",RED,50)
            scr.center_text((int(MAX_X/2),int(MAX_Y/2)+100),"click to restart",BLACK,20)
            gameover = True
 
        pygame.display.update()
        msElapsed = clock.tick(FPS) # TODO: Gamespeed should be FPS-independent
    
        
if __name__ == '__main__': main()
