#!/usr/bin/python

import pygame
from pygame.locals import *
import Vec2D
from Vec2D import *
import random

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
MAGENTA = (255,0,255)
CYAN = (0,255,255)
YELLOW = (255,255,0)

SHAPES = ('circle','triangle','square')

MAXSTATIONS = 15

LINES = [YELLOW,MAGENTA,CYAN,GREEN,BLUE,RED]

CARWITH = 10     # actually half of it
CARLENGTH = 20   # actually half of it
CARSPEED = 3
CARCAPACITY = 1

STATIONSIZE = 17
STATIONTHICKNESS = 5
STATIONDISTANCE = CARLENGTH * 4

PASSANGERSIZE = 7
PASSENGERPROBABILITY = .001
MAXWAITING = 5

RIGHT_OFFSET = int(MAXWAITING * STATIONSIZE) 

MAX_Y = 500
MAX_X = MAX_Y + RIGHT_OFFSET

FPS = 30

score = 0
gameover = False

screen = pygame.display.set_mode((MAX_X, MAX_Y))

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
	#poly = ((pos[0],pos[1]-size),
	#	(pos[0]+x,pos[1]+b),
	#	(pos[0]-x,pos[1]+b))
	pygame.draw.polygon(screen,color,poly,0)
		
def draw_square(pos,size,color,angle=0):
	"""draw square at pos with size in color"""
	rect = pygame.Rect(pos[0]-size,pos[1]-size,
					   size*2,size*2)
	pygame.draw.rect(screen,color,rect)
	

class Car():
	"""A railcar. Each track holds at least one"""
	
	def __init__(self,track):
		self.track = track
		self.pos = track.startpos
		self.direction = 1
		self.counter = 0
		self.poly = ((-CARWITH,-CARLENGTH),(-CARWITH,CARLENGTH),
		   			 (CARWITH,CARLENGTH),(CARWITH,-CARLENGTH))
		self.passengers = []
		self.angle = 0
			
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
			
	
	def draw(self):
		"""draw the car."""

		moved = self.move()
		pygame.draw.polygon(screen,self.track.color,moved,0)
		for p in self.passengers:
			p.draw(self.pos,self.angle)

class Track():
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
		
	def get_newpos(self,pos,count,direction=1):
		""" calculates new position of a car in direction. 
		direction should be 1 or -1"""
		
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
	
		

class Line():
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
		
	def update(self):
		for t in self.tracks:
			if t.cars:
				for c in t.cars:
					self.update_car(t,c)

	def update_car(self,track,car):
		"""calculate new position of cars"""
		global score # TODO: ugly
		
		car.pos = track.get_newpos(car.pos,car.counter,car.direction)

		if track.is_end(car.pos):
			
			# moving passengers
			station = get_station(car.pos)
			platform = [] # just for intermediate memory
			for p in car.passengers:
				if p.leave_at(station):
					# p leaves the car
					car.passengers.remove(p) # TODO: PERFORMANCE
					if p.shape == station.shape:
						score += 1
						print "Score: ", score
					else:
						# transition
						platform.append(p) 
			for p in station.passengers:
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
					# print "NEW DIRECTION: ", car.direction
				
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

class Passenger():
	"""they want to travel!"""
	
	def __init__(self,station):
		self.station = station
		shapes = list(SHAPES) # copy list
		shapes.remove(station.shape)
		self.shape = random.choice(shapes)
		self.car = None

	def draw(self,pos,angle=0):
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
			# stupid passenger: sits in car if shape is on line
			if self.shape in self.car.track.line:
				return False
			
			# stupid passenger: leaves if another line here
			if len(station.get_lines()) > 1:					
				return True

		return False

class Station():
	"""a station"""

	def __init__(self,pos,shape=''):
		if not shape:
			shape = random.choice(SHAPES)
		self.shape = shape
		self.pos = pos
		self.passengers = []
		# self.passengers = [Passenger(self)]
		
	def add_passenger(self):
		passengers.append(Passenger(self))
		
	def draw(self):
		size = 20
		pos = self.pos

		# TODO: calculate area of shapes to make it same size optical 
		#		dont use this ugly constants anymore
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
		if random.random() < PASSENGERPROBABILITY:
			if len(self.passengers) < MAXWAITING:
				self.passengers.append(Passenger(self))
			else:
				print "game over! Your score: ", score
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
		# print "length get_lines(): ", len(ret)			
		return ret


stations = []
lines = []

def init_city():
	"""we set some Stations in place."""

	print "Setting stations..."
	for i in range(0,MAXSTATIONS):
		foundpos = False
		while not foundpos:
			newstationpos = (random.randint(0 + 2 * STATIONSIZE, 
								   MAX_X - 2 * STATIONSIZE - RIGHT_OFFSET),
			        random.randint(0 + 2 * STATIONSIZE, 
								   MAX_Y - 2 * STATIONSIZE))
			print "trying position ", newstationpos
			foundpos = True
			for s in stations:
				if is_in_range(newstationpos,s.pos,STATIONDISTANCE):
					foundpos = False
					print "... is to near to ", s.pos
					
			if foundpos:
				print "position ok!"
				s = Station(newstationpos)
				stations.append(s)

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

def main():
	
	# this status is True if the user is drawing a track
	draw_status = False
	
	init_city()
	
	# Initialise screen
	pygame.init()
	clock = pygame.time.Clock()
	pygame.display.set_caption('Maxi Metro')
	pygame.display.update()

	pos = (0,0);
	startpos = (0,0)
	have_line = False
	line = ""
	# Event loop
	while 1: # not gameover:

		screen.fill(WHITE)
			
		# TODO: the whole handling of track-creation should be 
		#       in the Line-class
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == MOUSEBUTTONDOWN:
				draw_status = False
				if have_line:
					LINES.pop()
				have_line = False
				if LINES:
					pos = event.pos
					spos = is_station_pos(pos)
					if spos and not draw_status:
						#track = Track(spos)
						startpos = spos
						print "start drawing from " ,pos, " moving to ", startpos
						draw_status = True
				else:
					print "NO MORE LINES AVAIABLE!"
			elif event.type == MOUSEMOTION:
				pos = event.pos
				spos = is_station_pos(pos)
				# TODO: there should be no station in the way 
				#       (plus a little extrasize)
				# TODO: should not cross other tracks
				if draw_status and spos and not is_in_range(pos,startpos):
					print "stop drawing at " , pos , " moving to " , spos
					if have_line:
						print "appending track to line..."
						# startpos = spos

						line.tracks.append(Track(startpos,spos,line.color,line,0))
						line.stations.append(spos) # TODO: should not be double if circle
					else:
						print "creating new line..."
						line = Line(startpos, spos)
						lines.append(line)
						have_line = True
					startpos = spos
						# draw_status = False
			# elif event.type == MOUSEBUTTONUP:
		
		if draw_status:
			pygame.draw.line(screen,LINES[-1],startpos,pos,5)

		update()

		pygame.draw.line(screen,BLACK,(MAX_X-RIGHT_OFFSET,0),
									  (MAX_X-RIGHT_OFFSET,MAX_Y))
			
		# display all stations and tracks
		for l in lines:
			l.draw()		
		for s in stations:
			s.draw()
			
		pygame.display.update()
		msElapsed = clock.tick(FPS) # TODO: Gamespeed should be FPS-independent
		
		
if __name__ == '__main__': main()
