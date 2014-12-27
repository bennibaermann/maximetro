# -*- coding: utf-8 -*-
from Vec2D import *
import pygame
from pygame.locals import *
import pygame.gfxdraw

from config import *
from Util import *

class Screen(object):
    """here should happen all the drawing"""
    
    def __init__(self,lines):
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y + STATUSHEIGHT),RESIZABLE)
        self.lines = lines
        
        
    def getfont(self):
        font = pygame.font.match_font('freesans', bold=True)
        if font:
            return font
        else:
            if 'font' in DEBUG: print "Found no font, fallback to system font." 
            return pygame.font.get_default_font()


    def draw_image(self,image,pos,size,color,angle=0):
        image = pygame.image.load(image)
        image = pygame.transform.rotate(image,360-angle)
        w,h = image.get_size()
        pos = (pos[0]-w/2,pos[1]-h/2)
        self.screen.blit(image,pos)
    

    def draw_triangle(self,pos,size,color,angle=0):
        """draws an equilateral triangle in the outer circle at pos with size in color"""
        b = size / 2
        x = (size*size - b*b) ** .5
        
        triangle = ((0,-size),(x,b),(-x,b))
        if angle:
            triangle = rotate_poly(triangle,angle)
        poly = move_poly(triangle,pos)
        pygame.draw.polygon(self.screen,color,poly,0)
            
    
    
    def draw_square(self,pos,size,color,angle=0):
        """draw square at pos with size in color"""
    
        square = ((-size,-size),(-size,size),(size,size),(size,-size))
        if angle:
            square = rotate_poly(square,angle)
        rect = move_poly(square,pos)
        
        pygame.draw.polygon(self.screen,color,rect,0)
        
        
    def draw_rhombus(self,pos,size,color,angle=0):
        """draw rhombus at pos with size in color"""
        
        self.draw_square(pos,size,color,angle+45)
        
    
    def draw_semicircle(self,pos,size,color,angle=0):
        '''draws a semicircle at pos with size in color'''
        
        # rect = pygame.Rect(int(pos[0]-size/2),int(pos[1]-size/2),size,size)
        # pygame.draw.arc(self.screen,color,rect,0,math.pi/2,0)
        
        pygame.gfxdraw.filled_pie(self.screen,int(pos[0]),int(pos[1]),size,int(0+angle),int(180+angle),color)
        

    def center_text(self,pos,string,color=BLACK,size=FONTSIZE):
        """TODO BUGGY: prints string centered at pos"""
    
        font = pygame.font.Font(self.getfont(),size)
        text = font.render(string, True, color)
        rect = text.get_rect()
        pos = list(pos)
        pos[0] -= int(rect.width/2)
        pos[1] -= int(rect.height/2)
        self.screen.blit(text, pos)
    

    def text(self,pos,string,color=BLACK,size=FONTSIZE):
        """prints string in default font at pos"""
        
        font = pygame.font.Font(self.getfont(),size)
        text = font.render(string, True, color)
        self.screen.blit(text, pos)
    
    
    def pause(self):
        self.text((MAX_X-RIGHT_OFFSET+10,MAX_Y-60),"PAUSED")
        
    
    def waiting(self,waiting):
        div = float(waiting)/float(MAXWAITING+1)
        red = min(div * float(512),255)
        green = min(255,512 - div * float(512)) 
        color = (int(red),int(green),0)
        # flush_print(color)
        part = div * RIGHT_OFFSET
        rect = pygame.Rect(MAX_X-RIGHT_OFFSET,MAX_Y-20,int(part),20)
        pygame.draw.rect(self.screen,color,rect)
        self.text((MAX_X-RIGHT_OFFSET+10,MAX_Y-20),"WAITING: " + str(waiting))
        
    def score(self,score):
        self.text((MAX_X-RIGHT_OFFSET+10,MAX_Y-40),"$: " + str(score))
        
    def status(self,text):
        """draw a status text at the bottom line"""
        
        self.text((0,MAX_Y+4),text)
        
    def draw_interface(self):
        """draw the user interface"""
    
        # clear the interface aerea
        rect = pygame.Rect(MAX_X-RIGHT_OFFSET,0,RIGHT_OFFSET,MAX_Y)
        pygame.draw.rect(self.screen,WHITE,rect)
        rect = pygame.Rect(0,MAX_Y,MAX_X,STATUSHEIGHT)
        pygame.draw.rect(self.screen,WHITE,rect)
        
        # draw the +/- buttons
        count = 0
        for l in self.lines:
            rect = pygame.Rect(MAX_X-RIGHT_OFFSET,count*50,RIGHT_OFFSET,50)
            pygame.draw.rect(self.screen,l.color,rect)
            pygame.draw.rect(self.screen,BLACK,rect,1)
            self.center_text((MAX_X-int(RIGHT_OFFSET*.75),count*50+25),"-",BLACK,30)
            self.center_text((MAX_X-int(RIGHT_OFFSET*.25),count*50+25),"+",BLACK,30)        
            count += 1
    
        # draw separating lines
        pygame.draw.line(self.screen,BLACK,(MAX_X-RIGHT_OFFSET,0),
                                          (MAX_X-RIGHT_OFFSET,MAX_Y))
        pygame.draw.line(self.screen,BLACK,(int(MAX_X-RIGHT_OFFSET/2),0),
                                          (int(MAX_X-RIGHT_OFFSET/2),count*50-1))
        pygame.draw.line(self.screen,BLACK,(0,MAX_Y),(MAX_X,MAX_Y))
                                          


