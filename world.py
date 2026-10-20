"""Course layout, curves, map, scenery and perspective road renderer."""
import math
import random
import pygame
from config import *
from game.assets import assets


class World:
    def __init__(self):
        self.distance_traveled = 0.0
        self.finish_line_reached = False
        self.curve_profile = list(TRACK_CURVES)
        self.scenery = []
        for _ in range(SCENERY_COUNT):
            self.scenery.append({
                "kind": random.choice(("tree","palm","bush","sign","rock","building")),
                "distance": random.uniform(0, FINISH_LINE_DISTANCE),
                "side": random.choice([-1,1]),
                "offset": random.uniform(0.13,0.5),
                "color": random.choice([(28,105,38),(35,145,48),(22,85,32),(185,125,65)])
            })

    def reset(self):
        self.distance_traveled = 0.0
        self.finish_line_reached = False

    def curve_at(self, distance):
        for start, end, curve in self.curve_profile:
            if start <= distance < end:
                return curve
        return 0.0

    def update(self, player_speed, dt):
        if not self.finish_line_reached:
            self.distance_traveled += player_speed/3.6*dt
            if self.distance_traveled >= FINISH_LINE_DISTANCE:
                self.distance_traveled = FINISH_LINE_DISTANCE
                self.finish_line_reached = True

    def _curve_integral(self, start, end):
        if end <= start:
            return 0.0
        total = 0.0
        steps = max(1, int((end-start)/25))
        step = (end-start)/steps
        for i in range(steps):
            total += self.curve_at(start + (i+0.5)*step) * step
        return total

    def road_center_at_depth(self, depth):
        # Road is fixed near the player; upcoming curve integral shifts the horizon.
        start = self.distance_traveled
        end = min(FINISH_LINE_DISTANCE, start + max(0.0, depth))
        bend = self._curve_integral(start, end) * 0.10
        return SCREEN_WIDTH/2 - bend * (1.0 - min(1.0, depth/MAX_VISIBLE_DEPTH)*0.35)

    def project(self, depth):
        # depth=0 is foreground, larger depth approaches horizon.
        d = max(0.0, min(MAX_VISIBLE_DEPTH, depth))
        closeness = 1.0 - d/MAX_VISIBLE_DEPTH
        curve = closeness ** 1.65
        y = HORIZON_Y + curve*(SCREEN_HEIGHT-HORIZON_Y)
        width = ROAD_WIDTH_TOP + curve*(ROAD_WIDTH_BOTTOM-ROAD_WIDTH_TOP)
        return y, width, curve

    def _draw_sky(self, surface):
        # Only use a background image as the sky layer; the road and landscape
        # are rendered afterward. Never render sprite sheets as backgrounds.
        if assets.background(surface, ("backgrounds/mountain_background.jpg",
                                       "backgrounds/mountain_background.png")):
            return
        for y in range(HORIZON_Y+1):
            t = y/max(1,HORIZON_Y)
            c = tuple(int(a+(b-a)*t) for a,b in zip(COLOR_SKY_TOP,COLOR_SKY_BOTTOM))
            pygame.draw.line(surface,c,(0,y),(SCREEN_WIDTH,y))
        for cx,cy,rx,ry in [(90,105,42,11),(130,99,28,12),(535,138,50,12),(575,131,28,10)]:
            pygame.draw.ellipse(surface,(230,242,240),(cx-rx,cy-ry,rx*2,ry*2))
        # distant hills and city silhouette
        pygame.draw.polygon(surface,(105,170,165),[(0,HORIZON_Y-2),(75,HORIZON_Y-38),(150,HORIZON_Y-4),(245,HORIZON_Y-50),(340,HORIZON_Y-3),(445,HORIZON_Y-32),(555,HORIZON_Y-2),(675,HORIZON_Y-40),(800,HORIZON_Y-3),(800,HORIZON_Y+15),(0,HORIZON_Y+15)])
        x=0
        while x<SCREEN_WIDTH:
            bw=14+((x*7)%17); bh=12+((x*13)%38)
            pygame.draw.rect(surface,(120,160,180),(x,HORIZON_Y-bh,bw,bh))
            for wx in range(x+3,x+bw-2,7):
                for wy in range(HORIZON_Y-bh+4,HORIZON_Y-2,9):
                    pygame.draw.rect(surface,(205,225,225),(wx,wy,2,3))
            x+=bw+2

    def _draw_scenery(self,surface,obj):
        rel=(obj["distance"]-self.distance_traveled)
        if rel<0:
            rel += FINISH_LINE_DISTANCE
        if rel>MAX_VISIBLE_DEPTH:
            return
        y,w,curve=self.project(rel)
        center=self.road_center_at_depth(rel)
        scale=0.12+curve*1.0
        x=int(center+obj["side"]*(w/2+obj["offset"]*185*scale))
        y=int(y); kind=obj["kind"]; color=obj["color"]
        if y<HORIZON_Y-8 or y>SCREEN_HEIGHT+20 or x<-80 or x>SCREEN_WIDTH+80:
            return
        if kind in ("tree","palm"):
            trunk=max(4,int(30*scale)); r=max(4,int(23*scale))
            pygame.draw.rect(surface,(105,65,35),(x-max(1,int(3*scale)),y-trunk,max(2,int(7*scale)),trunk))
            if kind=="tree":
                pygame.draw.circle(surface,color,(x,y-trunk-r//2),r)
                pygame.draw.circle(surface,tuple(min(255,c+20) for c in color),(x-r//3,y-trunk-r//2),max(2,r//2))
            else:
                pygame.draw.line(surface,(105,75,35),(x,y-trunk),(x-r,y-trunk-r),max(1,int(3*scale)))
                pygame.draw.line(surface,(105,75,35),(x,y-trunk),(x+r,y-trunk-r),max(1,int(3*scale)))
                pygame.draw.line(surface,(30,135,45),(x,y-trunk),(x,y-trunk-int(r*1.5)),max(2,int(4*scale)))
        elif kind=="bush":
            r=max(3,int(15*scale)); pygame.draw.circle(surface,color,(x,y-r//2),r)
        elif kind=="sign":
            ph=max(5,int(28*scale)); sw=max(6,int(27*scale)); sh=max(5,int(17*scale))
            pygame.draw.rect(surface,(90,65,40),(x-2,y-ph,max(2,int(4*scale)),ph))
            pygame.draw.rect(surface,(20,100,100),(x-sw//2,y-ph-sh,sw,sh))
            pygame.draw.rect(surface,COLOR_WHITE,(x-sw//2,y-ph-sh,sw,sh),1)
        elif kind=="rock":
            r=max(3,int(14*scale)); pygame.draw.polygon(surface,(205,195,165),[(x-r,y),(x-r//2,y-r),(x+r//2,y-r),(x+r,y-r//3),(x+r//2,y)])
        elif kind=="building":
            bw=max(5,int(27*scale)); bh=max(5,int(42*scale))
            pygame.draw.rect(surface,(115,150,170),(x-bw//2,y-bh,bw,bh))

    def _draw_start_finish(self,surface, distance, is_start=False):
        # Project a stripe at the given distance relative to player.
        rel=distance-self.distance_traveled
        if rel < -8 or rel > MAX_VISIBLE_DEPTH:
            return
        y,w,curve=self.project(rel)
        center=self.road_center_at_depth(max(0,rel))
        left=int(center-w/2); cell=max(4,int(5+curve*11))
        for row in range(2):
            for col in range(max(1,int(w//cell))):
                colr=COLOR_WHITE if (row+col)%2==0 else COLOR_BLACK
                pygame.draw.rect(surface,colr,(left+col*cell,int(y)+row*max(3,cell//2),cell,max(3,cell//2)))
        if rel < 260:
            label="START" if is_start else "FINISH"
            # Small signboards near the roadside.
            for side in (-1,1):
                sx=int(center+side*(w/2+35+rel*0.12))
                sy=int(y-18-curve*12)
                pygame.draw.rect(surface,(35,35,40),(sx-2,sy,4,32))
                pygame.draw.rect(surface,(190,25,30),(sx-32,sy-19,64,19))
                pygame.draw.rect(surface,COLOR_WHITE,(sx-32,sy-19,64,19),1)

    def draw(self,surface,player_speed):
        self._draw_sky(surface)
        pygame.draw.rect(surface,COLOR_GRASS,(0,HORIZON_Y,SCREEN_WIDTH,SCREEN_HEIGHT-HORIZON_Y))
        # Moving grass stripes imply speed.
        stripe=int(self.distance_traveled*0.8)%54
        for y in range(HORIZON_Y+stripe-54,SCREEN_HEIGHT,108):
            pygame.draw.rect(surface,COLOR_GRASS_ALT,(0,max(HORIZON_Y,y),SCREEN_WIDTH,54))

        # Road strips from horizon to foreground; each strip bends according to course ahead.
        for i in range(ROAD_SEGMENTS):
            t0=i/ROAD_SEGMENTS; t1=(i+1)/ROAD_SEGMENTS
            y0=HORIZON_Y+t0*(SCREEN_HEIGHT-HORIZON_Y)
            y1=HORIZON_Y+t1*(SCREEN_HEIGHT-HORIZON_Y)
            c0=t0**1.65; c1=t1**1.65
            w0=ROAD_WIDTH_TOP+c0*(ROAD_WIDTH_BOTTOM-ROAD_WIDTH_TOP)
            w1=ROAD_WIDTH_TOP+c1*(ROAD_WIDTH_BOTTOM-ROAD_WIDTH_TOP)
            d0=(1-t0)*MAX_VISIBLE_DEPTH; d1=(1-t1)*MAX_VISIBLE_DEPTH
            center0=self.road_center_at_depth(d0)
            center1=self.road_center_at_depth(d1)
            phase=(i+int(self.distance_traveled/16))%2
            road_color=COLOR_ROAD if phase==0 else COLOR_ROAD_ALT
            sh0,sh1=w0*0.075,w1*0.075
            pygame.draw.polygon(surface,COLOR_SHOULDER,[(center0-w0/2-sh0,y0),(center0-w0/2,y0),(center1-w1/2,y1),(center1-w1/2-sh1,y1)])
            pygame.draw.polygon(surface,COLOR_SHOULDER,[(center0+w0/2,y0),(center0+w0/2+sh0,y0),(center1+w1/2+sh1,y1),(center1+w1/2,y1)])
            pygame.draw.polygon(surface,road_color,[(center0-w0/2,y0),(center0+w0/2,y0),(center1+w1/2,y1),(center1-w1/2,y1)])
            edge0,edge1=max(1,w0*0.012),max(2,w1*0.012)
            pygame.draw.polygon(surface,COLOR_WHITE,[(center0-w0/2,y0),(center0-w0/2+edge0,y0),(center1-w1/2+edge1,y1),(center1-w1/2,y1)])
            pygame.draw.polygon(surface,COLOR_WHITE,[(center0+w0/2-edge0,y0),(center0+w0/2,y0),(center1+w1/2,y1),(center1+w1/2-edge1,y1)])
            if phase==0:
                for lane in range(1,ROAD_LANES):
                    frac=-0.5+lane/ROAD_LANES
                    x0,x1=center0+frac*w0,center1+frac*w1
                    d0w,d1w=max(1,w0*0.006),max(2,w1*0.006)
                    pygame.draw.polygon(surface,COLOR_WHITE,[(x0-d0w,y0),(x0+d0w,y0),(x1+d1w,y1),(x1-d1w,y1)])

        for obj in sorted(self.scenery,key=lambda item:item["distance"],reverse=True):
            self._draw_scenery(surface,obj)
        self._draw_start_finish(surface,0,True)
        self._draw_start_finish(surface,FINISH_LINE_DISTANCE,False)

    def draw_minimap(self,surface,rivals,player_progress):
        # Fixed mini-map panel; show course curves from current point to finish.
        x0,y0,w,h=SCREEN_WIDTH-154,66,136,170
        pygame.draw.rect(surface,(12,18,30),(x0,y0,w,h))
        pygame.draw.rect(surface,(235,235,220),(x0,y0,w,h),2)
        # Course route in normalized mini-map coordinates.
        points=[]
        sample_count=70
        for i in range(sample_count+1):
            dist=player_progress+(FINISH_LINE_DISTANCE-player_progress)*i/sample_count
            curve=self.curve_at(dist)
            px=x0+w/2
            # Cumulative curvature approximation gives the route an obvious winding shape.
            offset=0.0
            for start,end,c in self.curve_profile:
                if start<dist:
                    offset += c*max(0,min(dist,end)-start)
            py=y0+8+i*(h-16)/sample_count
            px=x0+w/2+max(-42,min(42,offset*0.055))
            points.append((int(px),int(py)))
        if len(points)>1:
            pygame.draw.lines(surface,(255,220,45),False,points,4)
        # Player marker at top/current progress; rival markers by progress.
        pygame.draw.circle(surface,(50,240,235),(int(points[0][0]),int(points[0][1])),5)
        for rival in rivals:
            ratio=max(0,min(1,(rival.progress-player_progress)/max(1,FINISH_LINE_DISTANCE-player_progress)))
            idx=min(sample_count,int(ratio*sample_count))
            pygame.draw.circle(surface,rival.color,points[idx],3)
        # Current curve indicator
        curve=self.curve_at(player_progress+160)
        label="LEFT" if curve < -0.18 else "RIGHT" if curve > 0.18 else "STRAIGHT"
        font=pygame.font.Font(None,18)
        surface.blit(font.render(label,True,COLOR_WHITE),(x0+8,y0+h-20))
