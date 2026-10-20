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

    def environment_at(self, distance=None):
        distance = self.distance_traveled if distance is None else distance
        if distance < 1000:
            return "ALPINE"
        if distance < 2050:
            return "DESERT"
        if distance < 3150:
            return "FOREST"
        return "COAST"

    def _draw_sky(self, surface):
        environment = self.environment_at()
        if environment == "ALPINE" and assets.background(
                surface, ("backgrounds/mountain_background.jpg", "backgrounds/mountain_background.png")):
            return
        palettes = {
            "DESERT": ((40, 105, 190), (255, 190, 115), (195, 145, 70)),
            "FOREST": ((25, 65, 120), (175, 205, 200), (45, 105, 90)),
            "COAST": ((25, 135, 220), (175, 230, 245), (65, 155, 165)),
        }
        top, bottom, ridge = palettes.get(environment, (COLOR_SKY_TOP, COLOR_SKY_BOTTOM, (105,170,165)))
        for y in range(HORIZON_Y+1):
            t = y/max(1,HORIZON_Y)
            color = tuple(int(a+(b-a)*t) for a,b in zip(top,bottom))
            pygame.draw.line(surface,color,(0,y),(SCREEN_WIDTH,y))
        if environment == "DESERT":
            pygame.draw.circle(surface,(255,222,145),(SCREEN_WIDTH-105,75),30)
            pygame.draw.polygon(surface,(190,135,75),[(0,HORIZON_Y-2),(100,120),(220,185),(360,110),(500,185),(650,130),(800,170),(800,HORIZON_Y+10),(0,HORIZON_Y+10)])
            pygame.draw.polygon(surface,(220,170,95),[(0,HORIZON_Y),(160,155),(285,HORIZON_Y),(520,145),(690,HORIZON_Y),(800,160),(800,HORIZON_Y+12),(0,HORIZON_Y+12)])
        elif environment == "FOREST":
            pygame.draw.polygon(surface,ridge,[(0,HORIZON_Y),(70,130),(140,HORIZON_Y-8),(240,105),(335,HORIZON_Y),(455,125),(555,HORIZON_Y),(670,110),(800,HORIZON_Y)])
            for x in range(0,SCREEN_WIDTH,38):
                height=22+(x*17%48)
                pygame.draw.polygon(surface,(24,75,48),[(x,HORIZON_Y),(x+18,HORIZON_Y-height),(x+36,HORIZON_Y)])
        elif environment == "COAST":
            pygame.draw.rect(surface,(65,165,195),(0,HORIZON_Y-22,SCREEN_WIDTH,25))
            pygame.draw.polygon(surface,(110,175,155),[(0,HORIZON_Y),(95,150),(190,HORIZON_Y),(360,135),(500,HORIZON_Y),(650,145),(800,HORIZON_Y)])
        else:
            pygame.draw.polygon(surface,ridge,[(0,HORIZON_Y-2),(75,HORIZON_Y-38),(150,HORIZON_Y-4),(245,HORIZON_Y-50),(340,HORIZON_Y-3),(445,HORIZON_Y-32),(555,HORIZON_Y-2),(675,HORIZON_Y-40),(800,HORIZON_Y-3),(800,HORIZON_Y+15),(0,HORIZON_Y+15)])

    def _draw_scenery(self, surface, obj):
        rel = obj["distance"] - self.distance_traveled
        if rel < 0:
            rel += FINISH_LINE_DISTANCE
        if rel > MAX_VISIBLE_DEPTH:
            return
        y, road_width, curve = self.project(rel)
        center = self.road_center_at_depth(rel)
        scale = 0.12 + curve
        x = int(center + obj["side"] * (road_width/2 + obj["offset"]*185*scale))
        y = int(y)
        kind = obj["kind"]
        if y < HORIZON_Y-8 or y > SCREEN_HEIGHT+20 or x < -100 or x > SCREEN_WIDTH+100:
            return

        # Individual transparent props only; do not blit the full scenery sheet.
        candidates = {
            "tree": ("scenery/tree_broadleaf_01.png", "scenery/tree_broadleaf_02.png",
                     "scenery/tree_pine_01.png", "scenery/tree_pine_02.png"),
            "palm": ("scenery/tree_pine_03.png", "scenery/tree_broadleaf_01.png"),
            "bush": ("scenery/bush_02.png",),
            "rock": ("scenery/rock_cluster_01.png", "scenery/bush_rock_01.png"),
            "sign": ("scenery/road_sign_curve.png", "scenery/road_sign_chevron.png"),
        }
        sizes = {
            "tree": (int(96*scale), int(132*scale)),
            "palm": (int(88*scale), int(125*scale)),
            "bush": (int(74*scale), int(52*scale)),
            "rock": (int(76*scale), int(50*scale)),
            "sign": (int(48*scale), int(66*scale)),
        }
        for path in candidates.get(kind, ()):
            sprite = assets.image(path)
            if sprite is not None:
                tw, th = max(8, sizes[kind][0]), max(8, sizes[kind][1])
                sprite = pygame.transform.smoothscale(sprite, (tw, th))
                surface.blit(sprite, (x-tw//2, y-th))
                return

        # Safe fallback if an asset cannot be loaded.
        color = obj["color"]
        if kind in ("tree", "palm"):
            trunk=max(4,int(30*scale)); radius=max(4,int(23*scale))
            pygame.draw.rect(surface,(105,65,35),(x-max(1,int(3*scale)),y-trunk,max(2,int(7*scale)),trunk))
            pygame.draw.circle(surface,color,(x,y-trunk-radius//2),radius)
            pygame.draw.circle(surface,tuple(min(255,v+20) for v in color),
                               (x-radius//3,y-trunk-radius//2),max(2,radius//2))
        elif kind=="bush":
            radius=max(3,int(15*scale)); pygame.draw.circle(surface,color,(x,y-radius//2),radius)
        elif kind=="sign":
            ph=max(5,int(28*scale)); sw=max(6,int(27*scale)); sh=max(5,int(17*scale))
            pygame.draw.rect(surface,(90,65,40),(x-2,y-ph,max(2,int(4*scale)),ph))
            pygame.draw.rect(surface,(20,100,100),(x-sw//2,y-ph-sh,sw,sh))
            pygame.draw.rect(surface,COLOR_WHITE,(x-sw//2,y-ph-sh,sw,sh),1)
        elif kind=="rock":
            radius=max(3,int(14*scale))
            pygame.draw.polygon(surface,(205,195,165),[(x-radius,y),(x-radius//2,y-radius),
                (x+radius//2,y-radius),(x+radius,y-radius//3),(x+radius//2,y)])
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
        environment = self.environment_at()
        ground = {"ALPINE": COLOR_GRASS, "DESERT": (174,132,64), "FOREST": (25,92,42), "COAST": (65,155,115)}[environment]
        ground_alt = {"ALPINE": COLOR_GRASS_ALT, "DESERT": (195,151,76), "FOREST": (35,112,52), "COAST": (80,170,125)}[environment]
        road_base = {"ALPINE": COLOR_ROAD, "DESERT": (82,68,58), "FOREST": (47,53,53), "COAST": (62,66,72)}[environment]
        road_alt = {"ALPINE": COLOR_ROAD_ALT, "DESERT": (91,76,64), "FOREST": (55,61,60), "COAST": (72,76,82)}[environment]
        pygame.draw.rect(surface,ground,(0,HORIZON_Y,SCREEN_WIDTH,SCREEN_HEIGHT-HORIZON_Y))
        # Moving grass stripes imply speed.
        speed_ratio = max(0.0, min(1.35, player_speed / max(1.0, PLAYER_MAX_SPEED)))
        # Roadside bands and lane dash phases move faster at higher speeds.
        stripe=int(self.distance_traveled*(0.8 + speed_ratio*2.8))%108
        for y in range(HORIZON_Y+stripe-108,SCREEN_HEIGHT,108):
            pygame.draw.rect(surface,ground_alt,(0,max(HORIZON_Y,y),SCREEN_WIDTH,54))

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
            phase=(i+int(self.distance_traveled*(0.9 + speed_ratio*2.5)/16))%2
            road_color=road_base if phase==0 else road_alt
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
        if self.distance_traveled < 100:
            self._draw_start_finish(surface,90,True)
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
