"""Arcade HUD and bitmap text."""
import pygame
from config import *

GLYPHS = {
"A":(14,17,17,31,17,17,17),"B":(30,17,17,30,17,17,30),"C":(14,17,16,16,16,17,14),
"D":(30,17,17,17,17,17,30),"E":(31,16,16,30,16,16,31),"F":(31,16,16,30,16,16,16),
"G":(14,17,16,23,17,17,15),"H":(17,17,17,31,17,17,17),"I":(14,4,4,4,4,4,14),
"J":(7,2,2,2,18,18,12),"K":(17,18,20,24,20,18,17),"L":(16,16,16,16,16,16,31),
"M":(17,27,21,21,17,17,17),"N":(17,25,21,19,17,17,17),"O":(14,17,17,17,17,17,14),
"P":(30,17,17,30,16,16,16),"Q":(14,17,17,17,21,18,13),"R":(30,17,17,30,20,18,17),
"S":(15,16,16,14,1,1,30),"T":(31,4,4,4,4,4,4),"U":(17,17,17,17,17,17,14),
"V":(17,17,17,17,17,10,4),"W":(17,17,17,21,21,21,10),"X":(17,17,10,4,10,17,17),
"Y":(17,17,10,4,4,4,4),"Z":(31,1,2,4,8,16,31),
"0":(14,17,19,21,25,17,14),"1":(4,12,4,4,4,4,14),"2":(14,17,1,2,4,8,31),
"3":(30,1,1,14,1,1,30),"4":(2,6,10,18,31,2,2),"5":(31,16,16,30,1,1,30),
"6":(14,16,16,30,17,17,14),"7":(31,1,2,4,8,8,8),"8":(14,17,17,14,17,17,14),
"9":(14,17,17,15,1,1,14),":":(0,4,4,0,4,4,0),"'":(4,4,2,0,0,0,0),
"-":(0,0,0,31,0,0,0),".":(0,0,0,0,0,12,12),"/":(1,2,2,4,8,8,16),
"!":(4,4,4,4,4,0,4),"?":(14,17,1,2,4,0,4)," ": (0,0,0,0,0,0,0)
}


class PixelFont:
    def draw(self,surface,text,x,y,scale=3,color=COLOR_WHITE,shadow=True):
        cursor=int(x)
        for ch in str(text).upper():
            glyph=GLYPHS.get(ch,GLYPHS["?"])
            for row,bits in enumerate(glyph):
                for col in range(5):
                    if bits & (1<<(4-col)):
                        px,py=cursor+col*scale,int(y)+row*scale
                        if shadow:
                            pygame.draw.rect(surface,(15,18,28),(px+1,py+1,scale,scale))
                        pygame.draw.rect(surface,color,(px,py,scale,scale))
            cursor += 6*scale
        return cursor

    def number(self,surface,value,x,y,scale=3,color=COLOR_WHITE):
        return self.draw(surface,str(int(value)),x,y,scale,color)


class HUD:
    def __init__(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.font=PixelFont()
        self.pygame_font=pygame.font.Font(None,22)

    def _label(self,surface,text,x,y,bg,scale=2):
        w=len(text)*6*scale+10
        h=7*scale+8
        pygame.draw.rect(surface,bg,(x,y,w,h))
        pygame.draw.rect(surface,COLOR_WHITE,(x+2,y+2,w-4,h-4),1)
        self.font.draw(surface,text,x+5,y+4,scale,COLOR_BLACK,False)

    def draw(self,surface,time_left,speed,score,position,total_riders,distance,nitro,damage,vehicle_type="BIKE"):
        self.vehicle_label = vehicle_type
        self._label(surface,"TIME",12,9,(245,115,55))
        self.font.number(surface,max(0,time_left),78,12,3,COLOR_YELLOW)
        self._label(surface,"SCORE",195,9,COLOR_MAGENTA)
        self.font.number(surface,score,285,12,3,COLOR_WHITE)
        self._label(surface,"POS",535,9,COLOR_CYAN)
        self.font.draw(surface,f"{position}/{total_riders}",600,12,3,COLOR_YELLOW)

        # Speed, boost and bike condition
        self.font.number(surface,int(speed),20,SCREEN_HEIGHT-93,5,(255,65,60))
        self.font.draw(surface,"KM/H",23,SCREEN_HEIGHT-52,2,COLOR_WHITE)
        self._bar(surface,112,SCREEN_HEIGHT-44,180,14,speed/280.0,COLOR_CYAN)
        self.font.draw(surface,"NITRO",112,SCREEN_HEIGHT-65,2,COLOR_YELLOW)
        self._bar(surface,170,SCREEN_HEIGHT-64,122,10,nitro/100.0,(55,210,255))
        self.font.draw(surface,self.vehicle_label,315,SCREEN_HEIGHT-65,2,COLOR_WHITE)
        self._bar(surface,365,SCREEN_HEIGHT-64,90,10,1-damage/100.0,(70,230,90))
        self.font.draw(surface,"DIST",SCREEN_WIDTH-135,SCREEN_HEIGHT-70,2,COLOR_WHITE)
        self.font.number(surface,max(0,int(distance)),SCREEN_WIDTH-135,SCREEN_HEIGHT-48,2,COLOR_YELLOW)

    def _bar(self,surface,x,y,w,h,ratio,color):
        pygame.draw.rect(surface,(15,18,25),(x,y,w,h))
        pygame.draw.rect(surface,COLOR_WHITE,(x,y,w,h),1)
        fill=int((w-4)*max(0,min(1,ratio)))
        if fill:
            pygame.draw.rect(surface,color,(x+2,y+2,fill,h-4))
