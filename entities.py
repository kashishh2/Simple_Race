"""Player and AI rivals for Highway Rush."""
import random
import pygame
from config import *
from game.assets import assets


def clamp(value, low, high):
    return max(low, min(high, value))


class Car:
    def __init__(self, color):
        self.color = color
        self.lane = 0.0
        self.speed = 0.0
        self.progress = 0.0
        self.ai_lane_target = 0.0
        self.base_width = 76
        self.base_height = 50
        self.name = "RIVAL"

    def draw(self, surface, x, y, scale, is_player=False):
        if scale <= 0:
            return
        w = max(8, int(self.base_width * scale))
        h = max(7, int(self.base_height * scale))
        x, y = int(x), int(y)
        left, top = x - w // 2, y - h

        wheel_w, wheel_h = max(2, w // 8), max(2, h // 3)
        pygame.draw.rect(surface, COLOR_BLACK, (left + w // 10, y - wheel_h, wheel_w, wheel_h))
        pygame.draw.rect(surface, COLOR_BLACK, (left + w - w // 10 - wheel_w, y - wheel_h, wheel_w, wheel_h))

        # Rear body silhouette with angular fenders.
        pygame.draw.polygon(surface, (25, 22, 27), [
            (left + w//8, top + h//4), (left + w//4, top),
            (left + w*3//4, top), (left + w*7//8, top + h//4),
            (left + w, y - h//7), (left, y - h//7)
        ])
        pygame.draw.polygon(surface, self.color, [
            (left + w//8, top + h//4), (left + w//4, top + h//12),
            (left + w*3//4, top + h//12), (left + w*7//8, top + h//4),
            (left + w*15//16, y - h//7), (left + w//16, y - h//7)
        ])

        if scale > 0.24:
            win = pygame.Rect(left + w//4, top + h//9, max(3, w//2), max(2, h//4))
            pygame.draw.rect(surface, (20, 38, 58), win)
            pygame.draw.rect(surface, (95, 185, 220), win.inflate(-max(1,w//12), -max(1,h//12)))
            light_w, light_h = max(2,w//7), max(2,h//8)
            pygame.draw.rect(surface, (255,35,30), (left+w//12, y-h//3, light_w, light_h))
            pygame.draw.rect(surface, (255,35,30), (left+w-w//12-light_w, y-h//3, light_w, light_h))
            pygame.draw.rect(surface, (28,25,28), (left+w//8, y-max(2,h//8), w*3//4, max(2,h//8)))


class Player(Car):
    def __init__(self):
        super().__init__(COLOR_RED)
        self.speed = 0.0
        self.lane = 0.0
        self.progress = 0.0
        self.base_width = 250
        self.base_height = 122
        self.damage = 0
        self.hit_timer = 0.0
        self.nitro = 100.0
        self.nitro_active = False
        self.steering_direction = 0
        self.vehicle_type = "BIKE"

    def update(self, keys, dt, curve=0.0):
        accelerating = keys[pygame.K_UP] or keys[pygame.K_w]
        braking = keys[pygame.K_DOWN] or keys[pygame.K_s]
        self.nitro_active = (keys[pygame.K_SPACE] and self.nitro > 0 and accelerating)

        if accelerating:
            self.speed += PLAYER_ACCEL * dt
        elif braking:
            self.speed -= PLAYER_BRAKE * dt
        else:
            self.speed -= PLAYER_DRAG * dt

        if self.nitro_active:
            self.speed += 95.0 * dt
            self.nitro = max(0.0, self.nitro - 26.0 * dt)
        else:
            self.nitro = min(100.0, self.nitro + 5.0 * dt)

        self.speed = clamp(self.speed, 0.0, PLAYER_MAX_SPEED + (45 if self.nitro_active else 0))
        steer = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.steering_direction = steer
        # The course pulls the rider outward through a bend; steering counters it.
        curve_drift = curve * (self.speed / max(1.0, PLAYER_MAX_SPEED)) * 0.20
        self.lane = clamp(self.lane + (steer * PLAYER_STEER - curve_drift) * dt,
                          -MAX_LANE, MAX_LANE)
        self.hit_timer = max(0.0, self.hit_timer - dt)

    def _draw_car_player(self, surface, center_x):
        sprite, _ = assets.first(("cars/player_car.png", "cars/player_car_rear.png",
                                  "traffic/player_car.png"))
        if sprite is not None:
            iw, ih = sprite.get_size()
            factor = min(250/max(1,iw), 180/max(1,ih))
            sprite = pygame.transform.smoothscale(sprite, (max(1,int(iw*factor)), max(1,int(ih*factor))))
            surface.blit(sprite, (int(center_x-sprite.get_width()/2), SCREEN_HEIGHT-10-sprite.get_height()))
            return
        bottom = SCREEN_HEIGHT - 14
        w, h = 250, 126
        left, top = int(center_x - w/2), bottom-h
        pygame.draw.ellipse(surface, (25,35,30), (left+12,bottom-17,w-24,23))
        # Tires
        pygame.draw.polygon(surface, (18,18,22), [(left+14,top+72),(left+48,top+70),(left+47,bottom-5),(left+18,bottom-5)])
        pygame.draw.polygon(surface, (18,18,22), [(left+w-48,top+70),(left+w-14,top+72),(left+w-18,bottom-5),(left+w-47,bottom-5)])
        body = (255,45,42) if self.hit_timer > 0 and int(self.hit_timer*16)%2 else (215,15,25)
        pygame.draw.polygon(surface, (70,8,15), [(left+12,top+48),(left+45,top+18),(left+w-45,top+18),(left+w-12,top+48),(left+w-2,bottom-20),(left+2,bottom-20)])
        pygame.draw.polygon(surface, body, [(left+24,top+44),(left+58,top+24),(left+w-58,top+24),(left+w-24,top+44),(left+w-18,bottom-30),(left+18,bottom-30)])
        # Cabin and back glass
        pygame.draw.polygon(surface, (105,10,18), [(left+67,top+24),(left+82,top+1),(left+w-82,top+1),(left+w-67,top+24)])
        pygame.draw.polygon(surface, (20,40,58), [(left+81,top+8),(left+91,top+5),(left+w-91,top+5),(left+w-81,top+8),(left+w-72,top+31),(left+72,top+31)])
        pygame.draw.line(surface, (125,205,225), (left+91,top+11),(left+w-91,top+11),3)
        # Rear light bar, tail lamps, plate, bumper
        pygame.draw.rect(surface,(255,28,30),(left+24,top+51,49,17))
        pygame.draw.rect(surface,(255,28,30),(left+w-73,top+51,49,17))
        pygame.draw.rect(surface,(255,170,150),(left+30,top+55,35,4))
        pygame.draw.rect(surface,(255,170,150),(left+w-65,top+55,35,4))
        pygame.draw.rect(surface,(28,25,29),(left+15,bottom-31,w-30,13))
        pygame.draw.rect(surface,(235,232,215),(center_x-31,bottom-54,62,19))
        pygame.draw.rect(surface,(30,30,34),(center_x-25,bottom-50,50,11))
        pygame.draw.line(surface,(255,100,85),(left+28,top+43),(left+w-28,top+43),3)
        pygame.draw.circle(surface,(38,28,24),(center_x-28,top+4),8)
        pygame.draw.circle(surface,(255,220,40),(center_x+28,top+4),8)
    def _draw_bike_player(self, surface, center_x):
        # The three legacy "upright/lean" PNG paths currently contain the same
        # 3x2 contact sheet. Crop one frame instead of blitting the full sheet.
        direction = -1 if self.steering_direction < 0 else 1 if self.steering_direction > 0 else 0
        cache_key = "_bike_frames_cached"
        frames = getattr(self, cache_key, None)
        if frames is None:
            sheet, _ = assets.first(("bikes/player_bike_upright.png",
                                     "bikes/player_bike_lean_left.png",
                                     "bikes/player_bike_lean_right.png",
                                     "source_sheets/player_bike_sprite_sheet.png"))
            frames = {}
            if sheet is not None:
                sw, sh = sheet.get_size()
                # The committed artwork is a 3-column x 2-row contact sheet.
                cell_w, cell_h = sw // 3, sh // 2
                for key, col, row in (("left", 0, 0), ("upright", 1, 0), ("right", 2, 0)):
                    rect = pygame.Rect(col*cell_w, row*cell_h, cell_w, cell_h)
                    frame = sheet.subsurface(rect).copy().convert_alpha()
                    # Remove the light gray checkerboard around the sprite.
                    # Only neutral, bright pixels are keyed; colored bike/rider pixels remain.
                    for py in range(frame.get_height()):
                        for px in range(frame.get_width()):
                            r, g, b, a = frame.get_at((px, py))
                            if min(r, g, b) >= 155 and max(r, g, b)-min(r, g, b) <= 18:
                                frame.set_at((px, py), (r, g, b, 0))
                    frames[key] = frame
            setattr(self, cache_key, frames)

        frame_key = "left" if direction < 0 else "right" if direction > 0 else "upright"
        sprite = frames.get(frame_key) or frames.get("upright")
        if sprite is not None:
            iw, ih = sprite.get_size()
            factor = min(100/max(1, iw), 142/max(1, ih))
            sprite = pygame.transform.smoothscale(
                sprite, (max(1, int(iw*factor)), max(1, int(ih*factor))))
            surface.blit(sprite, (int(center_x-sprite.get_width()/2),
                                  SCREEN_HEIGHT-10-sprite.get_height()))
            return

        # Fallback: a compact motorcycle silhouette, never a car.
        cx, bottom = int(center_x), SCREEN_HEIGHT-12
        pygame.draw.ellipse(surface, (18,20,24), (cx-20,bottom-16,40,13))
        pygame.draw.circle(surface,(12,12,16),(cx,bottom-20),10,4)
        pygame.draw.line(surface,(210,20,32),(cx,bottom-30),(cx,bottom-72),7)
        pygame.draw.polygon(surface,(235,35,35),[(cx-8,bottom-55),(cx+8,bottom-55),(cx+15,bottom-34),(cx-15,bottom-34)])
        pygame.draw.circle(surface,(25,25,30),(cx,bottom-80),8)
        pygame.draw.line(surface,(235,35,35),(cx-14,bottom-69),(cx+14,bottom-69),5)
        if not getattr(self, "_bike_warned", False):
            print("[render] Bike art unavailable; using motorcycle silhouette.")
            self._bike_warned = True

    def draw_player(self, surface, center_x):
        if self.vehicle_type == "CAR":
            self._draw_car_player(surface, center_x)
        else:
            self._draw_bike_player(surface, center_x)



class Rival(Car):
    COLORS = [(35,95,235),(245,205,30),(35,185,80),(240,125,25),(235,235,225),(190,55,185),(20,180,190)]

    def __init__(self, index):
        super().__init__(random.choice(self.COLORS))
        self.index = index
        self.name = f"RIDER {index+1}"
        self.base_width = random.randint(66,82)
        self.base_height = random.randint(44,54)
        self.skill = random.uniform(0.88,1.12)
        self.aggression = random.uniform(0.35,0.95)
        self.change_timer = random.uniform(0.8,2.5)
        self.stamina = 100.0
        self.stunned = 0.0
        self.finished = False

    def set_grid_position(self, player_progress, offset, lane):
        self.progress = max(0.0, player_progress + offset)
        self.lane = lane
        self.ai_lane_target = lane
        self.speed = random.uniform(0, 25)
        self.finished = False

    def update_ai(self, player_progress, player_lane, player_speed, curve, dt, race_distance):
        if self.finished:
            return
        self.stunned = max(0.0, self.stunned-dt)
        self.change_timer -= dt

        # Bots accelerate hard from the grid, then target a skill-dependent pace.
        target_speed = random.uniform(176, 222) * self.skill
        if self.progress > player_progress + 250:
            target_speed *= 0.96
        if self.stunned <= 0:
            if self.speed < target_speed:
                self.speed = min(target_speed, self.speed + random.uniform(65,105)*dt)
            else:
                self.speed = max(target_speed-12, self.speed-24*dt)

        # Pick lanes periodically; react to nearby player and other riders.
        if self.change_timer <= 0:
            self.ai_lane_target = random.choice([-0.72, -0.36, 0.0, 0.36, 0.72])
            self.change_timer = random.uniform(0.7, 2.1) / self.skill
        if abs(self.progress-player_progress) < 130 and abs(self.lane-player_lane) < 0.25:
            self.ai_lane_target = clamp(player_lane + random.choice([-0.42,0.42]), -0.78, 0.78)
        # Riders drift outward in turns and actively counter-steer.
        self.lane += (self.ai_lane_target-self.lane)*min(1.0, dt*2.6)
        self.lane = clamp(self.lane - curve*0.06*dt, -0.86, 0.86)
        self.progress += self.speed / 3.6 * dt
        if self.progress >= race_distance:
            self.progress = race_distance
            self.finished = True
