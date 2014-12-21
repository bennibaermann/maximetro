# -*- coding: utf-8 -*-

# set which part of the game you want to debug, set all for maximum output
# DEBUG = ('init', 'font', 'track', 'path', 'station', 'passenger', 'random' )
DEBUG = ('init','font' )

# these basic gamemodes change the gameplay drastical
ANIMALS = False # an alternative animals graphic set from erlehmann
FREE_PASSENGERS = True # new passengers not at stations
STATION_PASSENGERS = False # new passengers at stations
BUILD_STATIONS = True # player can build new stations
DOUBLE_TRACKS = False # more than one track between same stations allowed?
CROSSING = False # crossing tracks allowed? TODO: Crossing=True does not work
COLLISION = False # set False if Cars should stop if other car is in the way

MAXWAITING = 80

BLACK =   (  0,   0,   0)
VERYLIGHTGREY= (220, 220, 220)
LIGHTGREY= (200, 200, 200)

WHITE =   (255, 255, 255)
BLUE =    (  0,   0, 255)
GREEN =   (  0, 255,   0)
RED =     (255,   0,   0)
MAGENTA = (255,   0, 255)
CYAN =    (  0, 255, 255)
YELLOW =  (255, 255,   0)

COLORS = [YELLOW,MAGENTA,CYAN,GREEN,BLUE,RED]
#COLORS = [CYAN,GREEN,BLUE,RED]
# LINES = list(COLORS)
COLORNAMES = ['red','blue','green','cyan','magenta','yellow']

SHAPES = ('circle','triangle','square')
OTHERSTATIONS = ('circle','triangle')
MAINSTATION = 'square'

MAXSTATIONS = 0 # stations build (without mainstation) during game init

PASSENGERSIZE = 7
PASSENGERSPEED = 0.3 # speed of passengers by foot
PASSENGER_RANDOMNESS = 0.01 # rate at which passenger in random mode changes direction
CARCAPACITY = 3

CARWITH = PASSENGERSIZE + 3        # actually half of it
CARLENGTH = 13 + PASSENGERSIZE * CARCAPACITY   # actually half of it
CARSPEED = 3

STATIONSIZE = 17
STATIONTHICKNESS = 5
STATIONDISTANCE = CARLENGTH * 3
MAXSTATIONTRACKS = 5 
STATIONTRACKDIST = 0 # TODO: minimal distance between tracks and center of station

PROBABILITY_START = .05
PROBABILITY_DIFF = .000005
# PROBABILITY_DIFF = 0
MAXWAITING_STATION = 9999


RIGHT_OFFSET = 200
#RIGHT_OFFSET = 200
MAX_Y = 800
MAX_X = MAX_Y + RIGHT_OFFSET
STATUSHEIGHT = 30 # height of status line at the bottom

MAX_DEPTH = 99999 # max distance for path finding (means no path)

FPS = 30

# money and prices
STARTMONEY = 50 # 30
STATIONCOST = 5
TRACKCOST = 1
DELETECOST = 1
# LINECOST = 5

FONTSIZE = 18 # size of the default font used