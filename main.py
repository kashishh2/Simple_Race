"""Simple Race: Highway Rush — course-based arcade racer."""
import sys
import pygame
from config import *
from entities import Player, Rival, clamp
from world import World
from ui import HUD, PixelFont


class Game:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock=pygame.time.Clock()
        self.running=True
        self.state="MENU"  # MENU, GRID, COUNTDOWN, RACING, FINISHED, GAMEOVER
        self.selected=0
        self.vehicle_type="BIKE"
        self.world=World()
        self.player=Player()
        self.player.vehicle_type=self.vehicle_type
        self.rivals=[Rival(i) for i in range(RIVAL_COUNT)]
        self.hud=HUD()
        self.font=PixelFont()
        self.score=0
        self.elapsed=0.0
        self.time_left=LEVEL_TIME_LIMIT
        self.countdown=3.0
        self.collision_cooldown=0.0
        self.message=""
        self.finish_order=[]
        self._reset_grid()

    def _reset_grid(self):
        # Staggered grid: opponents occupy multiple rows and lanes, not a single line ahead.
        offsets=[-18, 0, 22, 43, 64, 86, 108]
        lanes=[-0.55, 0.15, 0.58, -0.12, -0.62, 0.42, 0.0]
        for i,r in enumerate(self.rivals):
            r.set_grid_position(0.0,offsets[i],lanes[i])
        self.player.progress=0.0

    def reset(self):
        self.world.reset()
        self.player=Player()
        self.player.vehicle_type=self.vehicle_type
        self.rivals=[Rival(i) for i in range(RIVAL_COUNT)]
        self.score=0
        self.elapsed=0.0
        self.time_left=LEVEL_TIME_LIMIT
        self.countdown=3.0
        self.collision_cooldown=0.0
        self.finish_order=[]
        self._reset_grid()
        self.state="COUNTDOWN"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if self.state in ("RACING","COUNTDOWN","GRID"):
                        self.state="MENU"
                    else:
                        self.running=False
                elif self.state=="MENU":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected = (self.selected - 1) % 4
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected = (self.selected + 1) % 4
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        if self.selected == 1:
                            self.vehicle_type = "CAR" if self.vehicle_type == "BIKE" else "BIKE"
                    elif event.key == pygame.K_RETURN:
                        if self.selected == 0:
                            self.reset()
                        elif self.selected == 1:
                            self.vehicle_type = "CAR" if self.vehicle_type == "BIKE" else "BIKE"
                        elif self.selected == 2:
                            self.state = "CONTROLS"
                        else:
                            self.running = False
                elif self.state=="CONTROLS" and event.key in (pygame.K_RETURN,pygame.K_BACKSPACE):
                    self.state="MENU"
                elif self.state in ("FINISHED","GAMEOVER") and event.key in (pygame.K_r,pygame.K_RETURN):
                    if event.key==pygame.K_r:
                        self.reset()
                    else:
                        self.state="MENU"
                elif self.state=="GRID" and event.key==pygame.K_RETURN:
                    self.state="COUNTDOWN"

    def _current_position(self):
        # Rank is based on actual course progress, not just screen depth.
        progress=[self.player.progress]+[r.progress for r in self.rivals]
        return 1+sum(p>self.player.progress for p in progress[1:])

    def update(self,dt):
        dt=min(dt,0.05)
        if self.state=="COUNTDOWN":
            self.countdown-=dt
            if self.countdown<=0:
                self.state="RACING"
            return
        if self.state!="RACING":
            return

        curve=self.world.curve_at(self.player.progress+90)
        keys=pygame.key.get_pressed()
        self.player.update(keys,dt,curve)
        speed_factor=self.player.speed/3.6
        self.player.progress += speed_factor*dt
        self.world.distance_traveled=self.player.progress
        self.world.finish_line_reached=self.player.progress>=FINISH_LINE_DISTANCE
        self.elapsed+=dt
        self.time_left=max(0.0,LEVEL_TIME_LIMIT-self.elapsed)
        self.collision_cooldown=max(0.0,self.collision_cooldown-dt)

        for rival in self.rivals:
            rival_curve=self.world.curve_at(rival.progress+90)
            old_progress=rival.progress
            rival.update_ai(self.player.progress,self.player.lane,self.player.speed,rival_curve,dt,FINISH_LINE_DISTANCE)
            # Award points when the player passes a rival, not when the rival passes the player.
            if old_progress > self.player.progress and rival.progress <= self.player.progress:
                self.score += OVERTAKE_POINTS
            # Collision when cars are side-by-side in both lane and progress.
            if abs(rival.progress-self.player.progress)<9 and abs(rival.lane-self.player.lane)<0.23 and self.collision_cooldown<=0:
                self.player.speed*=0.58
                self.player.hit_timer=0.8
                self.player.damage=min(100,self.player.damage+14)
                rival.stunned=1.0
                rival.progress=max(0,rival.progress-18)
                self.collision_cooldown=COLLISION_COOLDOWN
                self.message="CRASH!"
                self.score=max(0,self.score-100)

        if self.world.finish_line_reached:
            self.player.progress=FINISH_LINE_DISTANCE
            self.state="FINISHED"
            self.finish_order=sorted([("YOU",self.player.progress)]+[(r.name,r.progress) for r in self.rivals],key=lambda p:p[1],reverse=True)
        elif self.time_left<=0 or self.player.damage>=100:
            self.state="GAMEOVER"

    def _draw_race(self):
        self.world.distance_traveled=self.player.progress
        self.world.draw(self.screen,self.player.speed)
        # Draw AI vehicles using their progress relative to the player.
        for rival in sorted(self.rivals,key=lambda r:r.progress,reverse=True):
            rel=rival.progress-self.player.progress
            if rel < -15 or rel > MAX_VISIBLE_DEPTH:
                continue
            # Camera projection: nearby rivals are lower/larger; far rivals near horizon.
            d=max(0.0,rel)
            y,w,curve=self.world.project(d)
            center=self.world.road_center_at_depth(d)
            x=center+rival.lane*w*0.43
            scale=0.17+curve*0.95
            if rel<0:
                y=min(SCREEN_HEIGHT-95,y+abs(rel)*0.3)
                scale=max(0.16,scale-abs(rel)*0.003)
            rival.draw(self.screen,x,y,scale,False)

        player_center=SCREEN_WIDTH/2+self.player.lane*205
        self.player.draw_player(self.screen,player_center)
        remaining=max(0,FINISH_LINE_DISTANCE-self.player.progress)
        self.hud.draw(self.screen,self.time_left,self.player.speed,self.score,
                      self._current_position(),RIVAL_COUNT+1,remaining,self.player.nitro,self.player.damage)
        self.world.draw_minimap(self.screen,self.rivals,self.player.progress)

        if self.state=="COUNTDOWN":
            shade=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
            shade.fill((0,0,0,65)); self.screen.blit(shade,(0,0))
            label="GO!" if self.countdown<0.8 else str(max(1,int(self.countdown)+1))
            self.font.draw(self.screen,label,SCREEN_WIDTH//2-35,SCREEN_HEIGHT//2-45,8,COLOR_YELLOW)
        if self.message and self.collision_cooldown>0:
            self.font.draw(self.screen,self.message,SCREEN_WIDTH//2-60,150,4,COLOR_RED)

    def _draw_menu(self):
        self.screen.fill((40,105,195))
        for y in range(HORIZON_Y):
            t=y/max(1,HORIZON_Y)
            c=(int(35+110*t),int(95+125*t),int(195+35*t))
            pygame.draw.line(self.screen,c,(0,y),(SCREEN_WIDTH,y))
        pygame.draw.rect(self.screen,COLOR_GRASS,(0,HORIZON_Y,SCREEN_WIDTH,SCREEN_HEIGHT-HORIZON_Y))
        pygame.draw.polygon(self.screen,COLOR_ROAD,[(370,HORIZON_Y),(430,HORIZON_Y),(690,600),(110,600)])
        self.font.draw(self.screen,"HIGHWAY RUSH",205,60,6,COLOR_YELLOW)
        self.font.draw(self.screen,"ROAD RACING",275,115,3,COLOR_WHITE)
        menu_items = ("START RACE", f"VEHICLE: {self.vehicle_type}", "CONTROLS", "QUIT")
        for i,label in enumerate(menu_items):
            y=225+i*48
            if i==self.selected:
                pygame.draw.rect(self.screen,(18,30,55),(190,y-7,420,38))
                pygame.draw.rect(self.screen,COLOR_CYAN,(190,y-7,420,38),2)
                self.font.draw(self.screen,">",208,y,3,COLOR_YELLOW)
            self.font.draw(self.screen,label,245,y,3,COLOR_WHITE)
        self.font.draw(self.screen,"LEFT/RIGHT CHANGE VEHICLE",220,440,2,COLOR_WHITE)

    def _draw_controls(self):
        self.screen.fill((25,45,80))
        self.font.draw(self.screen,"CONTROLS",275,90,5,COLOR_YELLOW)
        lines=["UP W ACCELERATE","DOWN S BRAKE","LEFT RIGHT STEER","SPACE NITRO BOOST","MENU LEFT/RIGHT VEHICLE","ENTER BACK"]
        for i,line in enumerate(lines):
            self.font.draw(self.screen,line,220,205+i*48,3,COLOR_WHITE)

    def _draw_end(self):
        shade=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
        shade.fill((5,8,20,200)); self.screen.blit(shade,(0,0))
        title="YOU WIN!" if self.state=="FINISHED" else "RACE OVER"
        self.font.draw(self.screen,title,270,175,6,COLOR_YELLOW)
        self.font.draw(self.screen,f"POSITION {self._current_position()}/{RIVAL_COUNT+1}",250,270,3,COLOR_WHITE)
        self.font.draw(self.screen,"SCORE",330,325,3,COLOR_CYAN)
        self.font.number(self.screen,self.score,350,360,5,COLOR_WHITE)
        self.font.draw(self.screen,"PRESS R TO RACE AGAIN",205,445,3,COLOR_YELLOW)
        self.font.draw(self.screen,"ENTER MENU",305,490,3,COLOR_WHITE)

    def draw(self):
        if self.state=="MENU":
            self._draw_menu()
        elif self.state=="CONTROLS":
            self._draw_controls()
        elif self.state in ("GRID","COUNTDOWN","RACING"):
            self._draw_race()
            if self.state=="GRID":
                self.font.draw(self.screen,"PRESS ENTER",290,240,4,COLOR_YELLOW)
        else:
            self._draw_race()
            self._draw_end()
        pygame.display.flip()

    def run(self):
        while self.running:
            dt=self.clock.tick(FPS)/1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit(0)


if __name__=="__main__":
    Game().run()
