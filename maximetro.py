#!/usr/bin/python

import pygame
from pygame.locals import *

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

STATIONSIZE = 17
STATIONTHICKNESS = 5

CARWITH = 10
CARLENGTH = 20
CARSPEED = 2

screen = pygame.display.set_mode((500, 500))


class Car():
	"""A railcar. Each track holds at least one"""
	
	def __init__(self,track):
		self.track = track
		self.pos = track.startpos
		self.direction = 0
		
	def draw(self):
		"""draw the car. should be a rectangle, but we use a circle for proof
		of concept now"""
		
		print "drawing car at ", self.pos
		pygame.draw.circle(screen,BLUE,self.pos,CARWITH)
		# pygame.draw.polygon(screen,BLUE,((10,10),(10,20),(20,20),(20,10)),0)

	def update(self):
		"""calculate new position of car"""
		
		self.pos = self.track.get_newpos(self.pos,self.direction)
		print "new position: ", self.pos


class Track():
	"""A railtrack between stations. Holds at minimum one Car"""
	
	def __init__(self,pos):
		# pygame.sprite.Sprite.__init__(self)
		self.startpos = pos
		self.endpos = pos
		self.cars = []
		self.cars.append(Car(self))
		
	def draw(self):
		pygame.draw.line(screen,RED,self.startpos,self.endpos,5)
		for c in self.cars:
			c.draw()

	def length(self):
		"""returns the length of the track"""
		
		#TODO: calculate only once if track changes
		start = self.startpos
		end = self.endpos
		return sqrt( (start[0]-end[0])**2 + (start[1]-end[1])**2 )
		
	def get_newpos(self,pos,dir=0):
		""" calculates new position of a car in direction. should be more 
		sophisticated with some trigonometry to ensure stable speed"""
		start = self.startpos
		end = self.endpos
		ret = list(pos)
		if pos[0] < end[0]:
			ret[0] += CARSPEED
		else:
			ret[0] -= CARSPEED
		if pos[1] < end[1]:
			ret[1] += CARSPEED
		else:
			ret[1] -= CARSPEED
		return ret
		

class Station():
	"""a station"""

	def __init__(self,pos,shape='circle'):
		self.shape = shape
		self.pos = pos
		
	def draw(self):
		size = 20
		pos = self.pos
		#		print "draw circle at pos: " , pos
		if self.shape == 'circle':
			pygame.draw.circle(screen,BLACK,pos,STATIONSIZE)
			pygame.draw.circle(screen,WHITE,pos,STATIONSIZE-STATIONTHICKNESS)


stations = Station((100,100)),Station((200,200))
tracks = []


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
	"""returns center of station if at pos is a station.
	this could maybe easier implemented with SpriteGroups?"""
	
	for s in stations:
		if is_in_range(pos,s.pos):
			return s.pos
	return False


def update():
	"""updates (position of) all user independent objects"""
	
	for t in tracks:
		for c in t.cars:
			c.update()


def main():

	# initialize global status
	draw_status = False

	# Initialise screen
	pygame.init()
	clock = pygame.time.Clock()
	pygame.display.set_caption('Maxi Metro')

	screen.fill(WHITE)
		
	# Blit everything to the screen
	#screen.blit(background, (0, 0))
	pygame.display.update()

	pos = (0,0);
	# Event loop
	while 1:

		screen.fill(WHITE)
			
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == MOUSEBUTTONDOWN:
				pos = event.pos
				spos = is_station_pos(pos)
				if spos and not draw_status:
					track = Track(spos)
					print "start drawing from " ,pos, " moving to ", track.startpos
					draw_status = True
			elif event.type == MOUSEMOTION:
				pos = event.pos
			elif event.type == MOUSEBUTTONUP:
				spos = is_station_pos(pos)
				if draw_status and spos:
					# pos = event.pos
					print "stop drawing at " , pos , " moving to " , spos
					# screen.fill(WHITE)
					track.endpos = spos
					tracks.append(track)
					draw_status = False
		
		if draw_status:
			# should be in track class
			pygame.draw.line(screen,BLACK,track.startpos,pos,5)

		update()

		# display all stations and tracks
		for t in tracks:
			t.draw()		
		for s in stations:
			s.draw()

		pygame.display.update()
		msElapsed = clock.tick(10)
		
		
if __name__ == '__main__': main()
