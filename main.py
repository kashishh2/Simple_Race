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
        for rival in self.rivals:
            rival.vehicle_type = self.vehicle_type
        self.hud=HUD()
        self.font=PixelFont()
        self.score=0
        self.center_score_timer=0.0
        self.elapsed=0.0
        self.time_left=LEVEL_TIME_LIMIT
        self.countdown=3.0
        self.collision_cooldown=0.0
        self.message=""
        self.message_timer=0.0
        self.curve_crash_timer=0.0
        self.curve_warning_timer=0.0
        self.curve_penalty_cooldown=0.0
        self.finish_order=[]
        self._reset_grid()

    def _reset_grid(self):
        # Staggered grid: opponents occupy multiple rows and lanes, not a single line ahead.
        offsets=[-18, 0, 22, 43, 64]
        lanes=[-0.55, 0.15, 0.58, -0.12, -0.62]
        for i,r in enumerate(self.rivals):
            r.set_grid_position(0.0,offsets[i],lanes[i])
        self.player.progress=0.0

    def reset(self):
        self.world.reset()
        self.player=Player()
        self.player.vehicle_type=self.vehicle_type
        self.rivals=[Rival(i) for i in range(RIVAL_COUNT)]
        for rival in self.rivals:
            rival.vehicle_type = self.vehicle_type
        self.score=0
        self.elapsed=0.0
        self.time_left=LEVEL_TIME_LIMIT
        self.countdown=3.0
        self.collision_cooldown=0.0
        self.curve_crash_timer=0.0
        self.curve_warning_timer=0.0
        self.curve_penalty_cooldown=0.0
        self.message=""
        self.message_timer=0.0
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
        # Progress is the single source of truth for both HUD rank and minimap.
        # Tiny tolerance prevents floating-point noise from swapping positions.
        return 1 + sum(r.progress > self.player.progress + 0.5 for r in self.rivals)

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
        upcoming_curve=self.world.curve_at(self.player.progress+190)
        keys=pygame.key.get_pressed()
        self.player.update(keys,dt,curve)

        # Reward holding a central racing line. Terrain drift means the rider must
        # counter-steer through bends instead of simply leaving the keys untouched.
        if self.player.speed >= 60.0 and abs(self.player.lane) <= 0.18:
            self.center_score_timer += dt
            if self.center_score_timer >= 1.0:
                earned = int(self.center_score_timer)
                self.score += earned * 25
                self.center_score_timer -= earned
        else:
            self.center_score_timer = 0.0

        # Warn before severe corners and enforce a safe cornering speed.
        warning_curve = upcoming_curve if abs(upcoming_curve) > abs(curve) else curve
        safe_corner_speed = 220.0 - min(1.0, abs(warning_curve)) * 105.0
        approaching_bend = abs(upcoming_curve) >= 0.45
        if approaching_bend and self.player.speed > safe_corner_speed - 18:
            self.curve_warning_timer = 1.0
            if self.message_timer <= 0.2:
                self.message = "CURVE AHEAD - SLOW DOWN!"
                self.message_timer = 0.7
        else:
            self.curve_warning_timer = max(0.0, self.curve_warning_timer-dt)

        # Smooth auto-braking increases with bend severity. Manual braking still helps.
        bend = abs(curve)
        if bend >= 0.18:
            auto_brake = (bend - 0.12) * 30.0
            self.player.speed = max(0.0, self.player.speed - auto_brake * dt)

        # Risk only accumulates while actually above a corner's safe speed.
        safe_corner_speed = 218.0 - min(1.0, bend) * 112.0
        over_speed = bend >= 0.38 and self.player.speed > safe_corner_speed
        if over_speed:
            excess_ratio = (self.player.speed-safe_corner_speed) / max(1.0, safe_corner_speed)
            self.curve_crash_timer += dt * min(1.6, 0.35 + excess_ratio*2.0)
        else:
            self.curve_crash_timer = max(0.0, self.curve_crash_timer-dt*2.5)

        # Penalize repeated high-speed cornering; never end the race mid-course.
        self.curve_penalty_cooldown = max(0.0, self.curve_penalty_cooldown-dt)
        if self.curve_crash_timer >= 1.4 and self.curve_penalty_cooldown <= 0.0:
            bend_direction = 1.0 if curve > 0 else -1.0
            self.player.lane = clamp(self.player.lane + bend_direction*0.10, -1.32, 1.32)
            self.player.damage = min(99, self.player.damage+8)
            self.score = max(0, self.score-150)
            self.player.speed *= 0.82
            self.player.hit_timer = 0.45
            self.curve_crash_timer = 0.0
            self.curve_penalty_cooldown = 2.0
            self.message = 'WIDE CORNER! -150 POINTS'
            self.message_timer = 1.4

        speed_factor=self.player.speed/3.6
        self.player.progress += speed_factor*dt
        self.world.distance_traveled=self.player.progress
        self.world.finish_line_reached=self.player.progress>=FINISH_LINE_DISTANCE
        self.elapsed+=dt
        self.time_left=max(0.0,LEVEL_TIME_LIMIT-self.elapsed)
        self.collision_cooldown=max(0.0,self.collision_cooldown-dt)
        self.message_timer=max(0.0,self.message_timer-dt)

        for rival in self.rivals:
            rival_curve=self.world.curve_at(rival.progress+90)
            old_rival_progress=rival.progress
            old_gap=old_rival_progress-(self.player.progress-speed_factor*dt)
            rival.update_ai(self.player.progress,self.player.lane,self.player.speed,rival_curve,dt,FINISH_LINE_DISTANCE)
            new_gap=rival.progress-self.player.progress

            # Award points exactly when the player passes a rival (ahead -> behind).
            if old_gap > 0 and new_gap <= 0:
                self.score += OVERTAKE_POINTS
                self.message = "OVERTAKE +250"
                self.message_timer = 1.15
            # A clean pass at high relative speed earns a small bonus.
            if old_gap > 0 and new_gap <= 0 and self.player.speed > rival.speed + 25:
                self.score += 100

            # Position is derived from actual progress; contact costs speed and points.
            if abs(rival.progress-self.player.progress)<9 and abs(rival.lane-self.player.lane)<0.23 and self.collision_cooldown<=0:
                self.player.speed*=0.58
                self.player.hit_timer=0.8
                self.player.damage=min(100,self.player.damage+14)
                rival.stunned=1.0
                rival.progress=max(0,rival.progress-18)
                self.collision_cooldown=COLLISION_COOLDOWN
                self.message="CRASH!"
                self.message_timer=0.9
                self.score=max(0,self.score-100)

        if self.world.finish_line_reached:
            self.player.progress=FINISH_LINE_DISTANCE
            self.state="FINISHED"
            self.finish_order=sorted([("YOU", self.player.progress, self.score)] + [(r.name, r.progress, 0) for r in self.rivals], key=lambda item:item[1], reverse=True)
        elif self.time_left<=0:
            self.finish_order=sorted([("YOU", self.player.progress, self.score)] + [(r.name, r.progress, 0) for r in self.rivals], key=lambda item:item[1], reverse=True)
            self.state="FINISHED"

    def _draw_race(self):
        self.world.distance_traveled=self.player.progress
        self.world.draw(self.screen,self.player.speed)
        # Draw AI vehicles using their progress relative to the player.
        for rival in sorted(self.rivals,key=lambda r:r.progress,reverse=True):
            rel=rival.progress-self.player.progress
            if rel < -15 or rel > MAX_VISIBLE_DEPTH:
                continue
            # Depth is relative to the player: rivals ahead shrink toward the
            # horizon; rivals behind move down the screen and grow.
            if rel >= 0:
                d=min(rel, MAX_VISIBLE_DEPTH)
                y, road_w, curve=self.world.project(d)
                center=self.world.road_center_at_depth(d)
                scale=0.12 + (1.0 - d/MAX_VISIBLE_DEPTH)**1.15 * 1.18
            else:
                behind=min(abs(rel), 300.0)
                y=min(SCREEN_HEIGHT-82, SCREEN_HEIGHT-145 + behind*0.34)
                road_w=ROAD_WIDTH_BOTTOM
                center=SCREEN_WIDTH/2
                scale=0.92 + (behind/300.0)*0.22
            x=center+rival.lane*road_w*0.43
            scale=max(0.12,min(1.30,scale))
            rival.draw(self.screen,x,y,scale,False)

        player_curve = self.world.curve_at(self.player.progress+20)
        player_center=SCREEN_WIDTH/2+self.player.lane*250-player_curve*62
        self.player.draw_player(self.screen,player_center)
        remaining=max(0,FINISH_LINE_DISTANCE-self.player.progress)
        self.hud.draw(self.screen,self.time_left,self.player.speed,self.score,
                      self._current_position(),RIVAL_COUNT+1,remaining,self.player.nitro,self.player.damage,self.vehicle_type)
        self.world.draw_minimap(self.screen,self.rivals,self.player.progress)

        if self.state=="COUNTDOWN":
            shade=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
            shade.fill((0,0,0,65)); self.screen.blit(shade,(0,0))
            label="GO!" if self.countdown<0.8 else str(max(1,int(self.countdown)+1))
            self.font.draw(self.screen,label,SCREEN_WIDTH//2-35,SCREEN_HEIGHT//2-45,8,COLOR_YELLOW)
        if self.message and self.message_timer>0:
            warning = "CURVE" in self.message or "BRAKE" in self.message or "CRASH" in self.message
            if not warning or int(self.message_timer*12)%2 == 0:
                msg_x = max(8, SCREEN_WIDTH//2-len(self.message)*6)
                self.font.draw(self.screen,self.message,msg_x,150,2,COLOR_YELLOW if warning else COLOR_CYAN)
            if self.curve_warning_timer > 0 and int(self.curve_warning_timer*14)%2 == 0:
                pygame.draw.rect(self.screen,COLOR_RED,(8,100,SCREEN_WIDTH-16,4),2)

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
        self.font.draw(self.screen,f"POSITION {self._current_position()}/{RIVAL_COUNT+1}",250,230,3,COLOR_WHITE)
        self.font.draw(self.screen,"FINAL SCOREBOARD",240,270,3,COLOR_CYAN)
        self.font.draw(self.screen,f"YOUR SCORE {self.score}",285,295,2,COLOR_YELLOW)
        board = self.finish_order or sorted([("YOU", self.player.progress, self.score)] + [(r.name, r.progress, 0) for r in self.rivals], key=lambda item:item[1], reverse=True)
        for rank, entry in enumerate(board[:RIVAL_COUNT+1], start=1):
            name, progress, points = entry
            row_y = 325 + (rank-1)*23
            row_color = COLOR_YELLOW if name == "YOU" else COLOR_WHITE
            self.font.draw(self.screen,f"{rank}. {name}",185,row_y,2,row_color)
            self.font.draw(self.screen,f"{int(progress):4d}M",445,row_y,2,COLOR_CYAN)
        self.font.draw(self.screen,"PRESS R TO RACE AGAIN",205,475,2,COLOR_YELLOW)
        self.font.draw(self.screen,"ENTER MENU",305,510,2,COLOR_WHITE)

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
