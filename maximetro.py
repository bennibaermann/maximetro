#!/usr/bin/python
# (c) 2014, Benni Baermann http://bennibaermann.de/
# COPYING: See LICENSE. This program is Free Software under AGPL

import pygame
from pygame.locals import *
import Vec2D
from Vec2D import *
import random

##################################################################
# configuration section
##################################################################

BLACK =   (  0,   0,   0)
WHITE =   (255, 255, 255)
BLUE =    (  0,   0, 255)
GREEN =   (  0, 255,   0)
RED =     (255,   0,   0)
MAGENTA = (255,   0, 255)
CYAN =    (  0, 255, 255)
YELLOW =  (255, 255,   0)

SHAPES = ('circle','triangle','square')
OTHERSTATIONS = ('circle','triangle')
MAINSTATION = 'square'

MAXSTATIONS = 8

COLORS = [YELLOW,MAGENTA,CYAN,GREEN,BLUE,RED]
#COLORS = [CYAN,GREEN,BLUE,RED]
LINES = list(COLORS)
COLORNAMES = ['red','blue','green','cyan','magenta','yellow']

PASSANGERSIZE = 7
CARCAPACITY = 3

CARWITH = PASSANGERSIZE + 3        # actually half of it
CARLENGTH = 13 + PASSANGERSIZE * CARCAPACITY   # actually half of it
CARSPEED = 3

STATIONSIZE = 17
STATIONTHICKNESS = 5
STATIONDISTANCE = CARLENGTH * 4

PROBABILITY_START = .005
#PROBABILITY_DIFF = .000001
PROBABILITY_DIFF = 0
MAXWAITING = 5

DOUBLE_TRACKS = False # more than one track between same stations allowed?
CROSSING = False # crossing tracks allowed?
COLLISION = False # set False if Cars should stop if other car is in range

RIGHT_OFFSET = int(MAXWAITING * STATIONSIZE) 
#RIGHT_OFFSET = 200
MAX_Y = 800
MAX_X = MAX_Y + RIGHT_OFFSET

FPS = 30

################################################################
# global variables
################################################################

score = 0
count = 0
gameover = False

screen = pygame.display.set_mode((MAX_X, MAX_Y))

semaphore = [] # sorage for cars with possible COLLISION
stations = []
lines = []

################################################################
# global functions
################################################################

def intersect( track,start,end ):
    """Calculates the intersection of line P1-P2 with P3-P4."""

    x1, y1 = track.startpos
    x2, y2 = track.endpos
    x3, y3 = start
    x4, y4 = end
    
    try:
        # code from https://twitter.com/mekkablue
        try:
            slope12 = ( float(y2) - float(y1) ) / ( float(x2) - float(x1) )
        except:
            slope12 = None
        try:
            slope34 = ( float(y4) - float(y3) ) / ( float(x4) - float(x3) )
        except:
            slope34 = None
            
        if slope12 == slope34:
            return False
        elif slope12 is None:
            # first line is vertical
            x = x1
            y = slope34 * ( x - x3 ) + y3
        elif slope34 is None:
            # second line is vertical
            x = x3
            y = slope12 * ( x - x1 ) + y1
        else:
            x = ( slope12 * x1 - y1 - slope34 * x3 + y3 ) / ( slope12 - slope34 )
            y = slope12 * ( x - x1 ) + y1
        
        # only true if intersection is between track.startpos and track.endpos
        x12_range = [x1,x2]
        y12_range = [y1,y2]
        x34_range = [x3,x4]
        y34_range = [y3,y4]
        x12_range.sort()
        y12_range.sort()    
        x34_range.sort()
        y34_range.sort()
        if x12_range[0] < x < x12_range[1] and \
           y12_range[0] < y < y12_range[1] and \
           x34_range[0] < x < x34_range[1] and \
           y34_range[0] < y < y34_range[1]:
            return True
        else:
            return False
        
    except Exception as e:
        print (str(e))
        return False
       
        
def intersect_any(start,end):
    """returns True if any intersection with existing tracks"""
    for l in lines:
        for t in l.tracks:
            if intersect(t,start,end):
                return True
    return False


def rotate_poly(pol,angle):
    """rotate polygon pol around (0,0) with angle and returns turned one"""

    # rotate car
    turnedpol = []
    for p in pol:
        v = Vec2d(p)
        turnedpol.append(v.rotated(angle))
    return turnedpol


def move_poly(poly,pos):
    """return a moved polygon shiftet with pos"""
    ret = []
    for p in poly:
        ret.append([p[0] + pos[0], p[1] + pos[1]])
    return ret


def draw_triangle(pos,size,color,angle=0):
    """draws an equilateral triangle in the outer circle at pos with size in color"""
    b = size / 2
    x = (size*size - b*b) ** .5
    
    triangle = ((0,-size),(x,b),(-x,b))
    if angle:
        triangle = rotate_poly(triangle,angle)
    poly = move_poly(triangle,pos)
    pygame.draw.polygon(screen,color,poly,0)
        
        
def draw_square(pos,size,color,angle=0):
    """draw square at pos with size in color"""

    square = ((-size,-size),(-size,size),(size,size),(size,-size))
    if angle:
        square = rotate_poly(square,angle)
    rect = move_poly(square,pos)
    
    pygame.draw.polygon(screen,color,rect,0)


def init_city():
    """we set some Stations in place."""
    
    print ("Setting main station...")
    stations.append(Station((int((MAX_X-RIGHT_OFFSET)/2), int (MAX_Y/2)),\
                            "square"))
    print ("Setting stations...")
    for i in range(0,MAXSTATIONS):
        foundpos = False
        while not foundpos:
            newstationpos = (random.randint(0 + 2 * STATIONSIZE, 
                                   MAX_X - 2 * STATIONSIZE - RIGHT_OFFSET),
                    random.randint(0 + 2 * STATIONSIZE, 
                                   MAX_Y - 2 * STATIONSIZE))
            print ("trying position ", newstationpos)
            foundpos = True
            for s in stations:
                if is_in_range(newstationpos,s.pos,STATIONDISTANCE):
                    foundpos = False
                    print ("... is to near to ", s.pos)
                    
            if foundpos:
                print( "position ok!")
                s = Station(newstationpos)
                stations.append(s)

 
def center_text(pos,string,color=BLACK,size=12):
    """TODO BUGGY: prints string centered at pos"""

    font = pygame.font.Font(pygame.font.get_default_font(),size)
    text = font.render(string, False, color)
    rect = text.get_rect()
    pos = list(pos)
    pos[0] -= int(rect.width/2)
    pos[1] -= int(rect.height/2)
    screen.blit(text, pos)


def text(pos,string,color=BLACK,size=12):
    """prints string in default font at pos"""
    
    font = pygame.font.Font(pygame.font.get_default_font(),size)
    text = font.render(string, False, color)
    screen.blit(text, pos)


def draw_interface():
    """draw the user interface"""

    count = 0
    for l in lines:
        rect = pygame.Rect(MAX_X-RIGHT_OFFSET,count*50,RIGHT_OFFSET,50)
        pygame.draw.rect(screen,l.color,rect)
        pygame.draw.rect(screen,BLACK,rect,1)
        center_text((MAX_X-int(RIGHT_OFFSET*.75),count*50+25),"-",BLACK,30)
        center_text((MAX_X-int(RIGHT_OFFSET*.25),count*50+25),"+",BLACK,30)        
        count += 1

    pygame.draw.line(screen,BLACK,(MAX_X-RIGHT_OFFSET,0),
                                      (MAX_X-RIGHT_OFFSET,MAX_Y))
    pygame.draw.line(screen,BLACK,(int(MAX_X-RIGHT_OFFSET/2),0),
                                      (int(MAX_X-RIGHT_OFFSET/2),count*50-1))
    
    text((MAX_X-RIGHT_OFFSET+10,MAX_Y-20),"SCORE: " + str(score))

        
def is_in_range(pos1,pos2,dist=STATIONSIZE):
    """returns true if pos1 and pos2 are not more than dist pixels apart"""
    
    if pos1[0] < pos2[0] - dist:
        return False
    if pos1[0] > pos2[0] + dist:
        return False        
    if pos1[1] < pos2[1] - dist:
        return False 
    if pos1[1] > pos2[1] + dist:
        return False 
    return True


def is_station_pos(pos):
    """returns center of station if at pos is a station."""
    
    for s in stations:
        if is_in_range(pos,s.pos):
            return s.pos
    return False


def get_station(pos):
    """returns station at position"""
    
    return next(s for s in stations if s.pos == is_station_pos(pos))


def update():
    """updates (position of) all user independent objects"""
    
    for l in lines:
        l.update()
    for s in stations:
        s.update()


def is_track(start,end):
    """returns True if there is any track betwen start and end"""

    for l in lines:
        for t in l.tracks:
            if t.startpos == start and t.endpos == end:
                return True
    return False

def for_all_cars(function):
    None


################################################################
# classes
################################################################

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
        self.waiting = False
            
            
    def move(self):
        """returns the moved polygon to self.pos with angle of self.track"""

        ret = []
        pol = self.poly

        # determine angle of track 
        # TODO: should calculated only once
        start = self.track.startpos
        end = self.track.endpos
        v = Vec2d(start[0]-end[0],start[1]-end[1])
        self.angle = v.get_angle() + 90
        
        # rotate car
        turnedpol = rotate_poly(pol,self.angle)
    
        # move to self.pos
        ret = move_poly(turnedpol,self.pos)
        
        return ret
        
            
    def car_in_range(self,pos):
        """returns a list with cars in range CARLENGTH from pos"""
        
        ret = []
        for l in lines:
            for t in l.tracks:
                for c in t.cars:
                    if c != self:
                        if is_in_range(c.pos,self.pos,CARLENGTH*2):
                            ret.append(c)
            
        return ret
    
    
    def want_move(self):
        """collision detection is handled here"""
        
        if COLLISION == True:
            return True
        else:
            future_pos = self.track.get_newpos(self.pos,self.counter,self.direction,CARLENGTH/CARSPEED)
            others = self.car_in_range(future_pos)
            if others:
                self.waiting = True
                ret = True
                for c in others:
                    if c.waiting:
                        ret = False
                        if not c in semaphore:
                            semaphore.append(c)
                        if not self in semaphore:
                            semaphore.append(self)
                 
                return ret
            else:
                return True
   
    
    def draw(self):
        """draw the car."""

        moved = self.move()
        pygame.draw.polygon(screen,self.track.color,moved,0)
        offset = CARCAPACITY/2 +1
        for p in self.passengers:
            offset -= 1
            p.draw(self.pos,offset,self.angle)



class Track(object):
    """A railtrack between stations."""
    
    def __init__(self,start,end,color,line,withcar=1):
        """constructor should only be called, if LINES[] is not empty"""
        # self.pos_in_line = pil
        self.line = line
        self.color = color
        self.startpos = start
        self.endpos = end
        self.cars = []
        if withcar:
            self.cars.append(Car(self))
            
        
    def draw(self):
        pygame.draw.line(screen,self.color,self.startpos,self.endpos,5)
        for c in self.cars:
            c.draw()
          
            
    def update(self):
        for c in self.cars:
            c.update()


    def length(self):
        """returns the length of the track"""
        
        #TODO: calculate only once if track changes
        start = self.startpos
        end = self.endpos
        return ( (start[0]-end[0])**2 + (start[1]-end[1])**2 ) ** .5
      
        
    def get_newpos(self,pos,count,direction=1,iter=1):
        """ calculates new position of a car in iter iterations"""
        
        start = self.startpos
        end = self.endpos
        ret = [0,0]
        length = self.length()
        xdiff = (start[0] - end[0]) / length * CARSPEED * iter * -1
        ydiff = (start[1] - end[1]) / length * CARSPEED * iter * -1
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
    
        

class Line(object):
    """A line contains multiple tracks between stations"""
    
    def __init__(self,start,end):
        self.color = LINES[-1]
        # self.colorname = COLORNAMES[-1]
        self.tracks = []
        self.tracks.append(Track(start,end,self.color,self))
        self.stations = [start,end]
        
        
    def is_circle(self):
        if self.tracks[0].startpos == self.tracks[-1].endpos:
            return True
        return False
        
        
    def update(self):
        if semaphore:
            c = semaphore.pop()
            c.waiting = False
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
            
            # moving passengers
            station = get_station(car.pos)
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
            for p in platform:
                station.passengers.append(p)
    
    
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
            track.cars.remove(car)
            next_track.add_car(car)
            car.counter = 0

        car.counter += 1
        
        
    def draw(self):
        for t in self.tracks:
            t.draw()
            

    def __contains__(self,shape):
        """returns True if Line contains stations with shape"""

        for pos in self.stations:
            station = get_station(pos)
            if shape == station.shape:
                return True
        return False
      
        
    def delete_track(self):
        """deletes the last track from the line"""
        
        print ("delete track from line color: ", self.color)
        track = self.tracks[-1]
        l = len(self.tracks)
        if track.cars and not l == 1:
            print ("we can't delete tracks with cars (unless last one)")
        else:
            self.tracks.pop()
            if l == 1:
                LINES.append(track.color)
        
        

class Passenger(object):
    """they want to travel to a station with shape self.shape!"""
    
    def __init__(self,station):
        self.station = station
        shapes = list(SHAPES) # copy list
        shapes.remove(station.shape)
        self.shape = random.choice(shapes)
        self.car = None


    def draw(self,pos,offset=0,angle=0):
        # generate vector in angle and length PASSANGERSIZE
        v = Vec2d(PASSANGERSIZE*3,0)
        v.rotate(angle+90)
        
        # add vector for every offset to pos
        v_pos = Vec2d(pos)
        v_new = v_pos + v * offset
        pos = (int(v_new.x),int(v_new.y))
        if self.shape == 'circle':
            pygame.draw.circle(screen,BLACK,pos,PASSANGERSIZE)
        elif self.shape == 'triangle':
            draw_triangle(pos,PASSANGERSIZE+1,BLACK,angle)
        elif self.shape == 'square':
            draw_square(pos,PASSANGERSIZE-1,BLACK,angle)


    def enter(self,car):
        """returns True if this passenger wants to enter this car"""
        
        return True


    def leave_at(self,station):
        """returns True if this passenger wants to leave the car at the station"""
        
        if station.shape == self.shape:
            return True
        
        if self.car:
            # TODO: we need some kind of recursive path finding here instead
            
            # stupid passenger: sits in car if shape is on line
            if self.shape in self.car.track.line:
                return False
            
            # stupid passenger: leaves if another line here
            if len(station.get_lines()) > 1:                    
                return True

        return False



class Station(object):
    """a station"""

    def __init__(self,pos,shape=''):
        if not shape:
            shape = random.choice(OTHERSTATIONS)
        self.shape = shape
        self.pos = pos
        self.passengers = []
        
        
    def add_passenger(self):
        passengers.append(Passenger(self))
        
        
    def draw(self):
        size = 20
        pos = self.pos

        # TODO: calculate area of shapes to make it same size optical 
        #        dont use this ugly constants anymore
        if self.shape == 'circle':
            pygame.draw.circle(screen,BLACK,pos,STATIONSIZE)
            pygame.draw.circle(screen,WHITE,pos,STATIONSIZE-STATIONTHICKNESS)
        if self.shape == 'triangle':
            draw_triangle(pos,STATIONSIZE+4,BLACK)
            draw_triangle(pos,STATIONSIZE+4-STATIONTHICKNESS*2,WHITE)
        if self.shape == 'square':
            draw_square(pos,STATIONSIZE-3,BLACK)
            draw_square(pos,STATIONSIZE-STATIONTHICKNESS-3,WHITE)

        count = 0
        for p in self.passengers:
            p.draw((pos[0]+int(STATIONSIZE*1.5)+STATIONSIZE*count,pos[1]))
            count += 1
               
                
    def update(self):
        global gameover
        global count
        if random.random() < PROBABILITY_START + count * PROBABILITY_DIFF:
            if len(self.passengers) < MAXWAITING:
                self.passengers.append(Passenger(self))
            else:
                gameover = True
              
                
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

########################################################################
# main programm
########################################################################
                        
def main():
    global count, lines, semaphores, stations, gameover, LINES, score
    # Initialise stuff
    init_city()
    pygame.init()
    pygame.display.set_caption('Maxi Metro')
    clock = pygame.time.Clock()
    
    pos = startpos = (0,0)
    have_line = draw_status = False
    line = None
    # Event loop
    while 1:
        count += 1
            
        # TODO: ugly code. we have to wrote some functions here
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if gameover:
                    # game restart
                    # TODO: should be function
                    gameover = False
                    stations = []
                    lines = []
                    semaphore = []
                    pos = startpos = (0,0)
                    have_line = draw_status = False
                    line = None
                    LINES = list(COLORS)
                    init_city()
                    score = 0
                else:
                    draw_status = False
                    if have_line:
                        LINES.pop()
                    have_line = False
                    if LINES:
                        pos = event.pos
                        spos = is_station_pos(pos)
                        if spos and not draw_status:
                            startpos = spos
                            print ("start drawing from " ,pos, " moving to ", startpos)
                            draw_status = True
                    else:
                        print ("NO MORE LINES AVAIABLE!")
                        
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
                                print ("add track to line with color ", color)
                                draw_status = have_line = True
                                line = lines[color]
                                LINES.append(line.color)
                                startpos = line.tracks[-1].endpos
                                
            elif event.type == MOUSEMOTION and not gameover:
                if not CROSSING and not intersect_any(startpos,event.pos):            
                    pos = event.pos
                    spos = is_station_pos(pos)
                    # TODO: there should be no station in the way 
                    #        (plus a little extrasize)
                    # TODO: should not cross other tracks
                    if draw_status and spos and not is_in_range(pos,startpos):
                        if not DOUBLE_TRACKS and not is_track(startpos,spos) and \
                           not is_track(spos,startpos):
                            print ("stop drawing at " , pos , " moving to " , spos)
                            if have_line:
                                print ("appending track to line...")
                                # startpos = spos
        
                                line.tracks.append(Track(startpos,spos,line.color,line,0))
                                line.stations.append(spos) # TODO: should not be double if circle
                            else:
                                print ("creating new line...")
                                line = Line(startpos, spos)
                                lines.append(line)
                                have_line = True
                            startpos = spos
        screen.fill(WHITE)

        draw_interface()
        
        for l in lines:
            l.draw()        
        if not gameover:
            if draw_status:
                pygame.draw.line(screen,LINES[-1],startpos,pos,5)
            update()
        for s in stations:
            s.draw()
        if gameover:    
            center_text((int(MAX_X/2),int(MAX_Y/2)),"GAME OVER!",BLACK,52)
            center_text((int(MAX_X/2),int(MAX_Y/2)),"GAME OVER!",RED,50)
            center_text((int(MAX_X/2),int(MAX_Y/2)+100),"click to restart",BLACK,20)
            
        
        pygame.display.update()
        msElapsed = clock.tick(FPS) # TODO: Gamespeed should be FPS-independent
    
        
if __name__ == '__main__': main()
