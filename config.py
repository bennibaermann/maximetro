# -*- coding: utf-8 -*-

DEBUG = False

# these basic gamemodes change the gameplay drastical
ANIMALS = False # an alternative animals graphic set from erlehmann
FREE_PASSENGERS = True # new passengers not at stations
STATION_PASSENGERS = False # new passengers at stations
BUILD_STATIONS = True # player can build new stations
DOUBLE_TRACKS = False # more than one track between same stations allowed?
CROSSING = False # crossing tracks allowed?
COLLISION = False # set False if Cars should stop if other car is in the way

BLACK =   (  0,   0,   0)
WHITE =   (255, 255, 255)
BLUE =    (  0,   0, 255)
GREEN =   (  0, 255,   0)
RED =     (255,   0,   0)
MAGENTA = (255,   0, 255)
CYAN =    (  0, 255, 255)
YELLOW =  (255, 255,   0)

COLORS = [YELLOW,MAGENTA,CYAN,GREEN,BLUE,RED]
#COLORS = [CYAN,GREEN,BLUE,RED]
LINES = list(COLORS)
COLORNAMES = ['red','blue','green','cyan','magenta','yellow']

SHAPES = ('circle','triangle','square')
OTHERSTATIONS = ('circle','triangle')
MAINSTATION = 'square'

MAXSTATIONS = 0

PASSENGERSIZE = 7
PASSENGERSPEED = 1 # speed of passengers by foot
CARCAPACITY = 2

CARWITH = PASSENGERSIZE + 3        # actually half of it
CARLENGTH = 13 + PASSENGERSIZE * CARCAPACITY   # actually half of it
CARSPEED = 3

STATIONSIZE = 17
STATIONTHICKNESS = 5
STATIONDISTANCE = CARLENGTH * 3
MAXSTATIONTRACKS = 5
STATIONTRACKDIST = 0 # TODO: minimal distance between tracks and center of station

PROBABILITY_START = .1
#PROBABILITY_DIFF = .000001
PROBABILITY_DIFF = 0
MAXWAITING = 10


RIGHT_OFFSET = int(MAXWAITING * STATIONSIZE) 
#RIGHT_OFFSET = 200
MAX_Y = 500
MAX_X = MAX_Y + RIGHT_OFFSET

MAX_DEPTH = 99999 # max distance for path finding (means no path)

FPS = 30
