# -*- coding: utf-8 -*-
from Vec2D import *

from config import *


# exceptions
class GameOver(Exception): pass

#
# global functions
#

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


def dist(pos1,pos2):
    """return distance between two positions"""
    
    v1 = Vec2d(pos1)
    v2 = Vec2d(pos2)
    v = v1-v2
    l = v.get_length()
    return l


def is_in_range(pos1,pos2,maxdist=STATIONSIZE):
    """returns true if pos1 and pos2 are not more than dist pixels apart"""

    d = dist(pos1,pos2)
    if d <= maxdist:
        return True
    return False
    