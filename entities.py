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
        x, y = int(x), int(y)
        vehicle_type = getattr(self, "vehicle_type", "CAR")
        if vehicle_type == "BIKE":
            # Draw one cropped bike frame for AI riders too; never use car geometry
            # in a motorcycle race.
            frames = getattr(self, "_bike_frames_cached", None)
            if frames is None:
                frames = {}
                sheet, _ = assets.first(("bikes/player_bike_upright.png",
                                         "source_sheets/player_bike_sprite_sheet.png"))
                if sheet is not None:
                    sw, sh = sheet.get_size()
                    cw, ch = sw // 3, sh // 2
                    for key, col in (("left", 0), ("upright", 1), ("right", 2)):
                        frame = sheet.subsurface(pygame.Rect(col*cw, 0, cw, ch)).copy().convert_alpha()
                        # Remove neutral light-grey checkerboard pixels around the art.
                        for py in range(frame.get_height()):
                            for px in range(frame.get_width()):
                                r, g, b, a = frame.get_at((px, py))
                                if min(r, g, b) >= 155 and max(r, g, b)-min(r, g, b) <= 18:
                                    frame.set_at((px, py), (r, g, b, 0))
                        frames[key] = frame
                self._bike_frames_cached = frames
            direction = -1 if self.lane < self.ai_lane_target-0.06 else 1 if self.lane > self.ai_lane_target+0.06 else 0
            sprite = frames.get("left" if direction < 0 else "right" if direction > 0 else "upright")
            if sprite is not None:
                iw, ih = sprite.get_size()
                max_w, max_h = max(7, int(100*scale)), max(9, int(142*scale))
                factor = min(max_w/max(1,iw), max_h/max(1,ih))
                sprite = pygame.transform.smoothscale(sprite, (max(1,int(iw*factor)), max(1,int(ih*factor))))
                # Tint the sprite while preserving its alpha channel, so no box is drawn.
                tint = getattr(self, "rider_color", self.color)
                tinted = sprite.copy().convert_alpha()
                overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
                overlay.fill((*tint, 255))
                tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                sprite = tinted
                # Bright number plate/marker remains readable even at small scale.
                surface.blit(sprite, (x-sprite.get_width()//2, y-sprite.get_height()))
                if scale > 0.35:
                    marker_y = y-sprite.get_height()-7
                    pygame.draw.circle(surface, tint, (x, marker_y), max(3,int(5*scale)))
                    pygame.draw.circle(surface, (245,245,235), (x, marker_y), max(3,int(5*scale)), 1)
                return
            # Compact motorcycle silhouette fallback.
            h, w = max(10,int(54*scale)), max(5,int(25*scale))
            pygame.draw.ellipse(surface, (12,12,16), (x-w//2,y-h//5,w,h//4))
            pygame.draw.line(surface, (210,25,35), (x,y-h//4), (x,y-h*4//5), max(2,int(4*scale)))
            pygame.draw.circle(surface, (20,20,24), (x,y-h//5), max(2,int(5*scale)), max(1,int(2*scale)))
            pygame.draw.circle(surface, (30,30,35), (x,y-h*4//5), max(2,int(4*scale)))
            return

        w = max(8, int(self.base_width * scale))
        h = max(7, int(self.base_height * scale))
        left, top = x - w // 2, y - h
        # Low, wide rear-view sports car; avoid tall bus-like proportions.
        w = max(8, int(self.base_width * scale))
        h = max(6, int(self.base_height * scale * 0.68))
        left, top = x - w // 2, y - h
        wheel_w, wheel_h = max(2, w // 10), max(3, h // 2)
        pygame.draw.rect(surface, (8, 9, 12), (left+w//9, y-wheel_h, wheel_w, wheel_h))
        pygame.draw.rect(surface, (8, 9, 12), (left+w-w//9-wheel_w, y-wheel_h, wheel_w, wheel_h))
        body = [
            (left+w//5, top+h//3), (left+w//3, top+h//10),
            (left+w*2//3, top+h//10), (left+w*4//5, top+h//3),
            (left+w*15//16, y-h//5), (left+w*9//10, y-h//12),
            (left+w//10, y-h//12), (left+w//16, y-h//5)
        ]
        pygame.draw.polygon(surface, (14, 15, 20), body)
        inner = [
            (left+w//5, top+h//3), (left+w//3, top+h//7),
            (left+w*2//3, top+h//7), (left+w*4//5, top+h//3),
            (left+w*14//16, y-h//5), (left+w*9//10, y-h//9),
            (left+w//10, y-h//9), (left+w//16, y-h//5)
        ]
        pygame.draw.polygon(surface, self.color, inner)
        glass = [
            (left+w//3, top+h//6), (left+w*2//3, top+h//6),
            (left+w*3//4, top+h//3), (left+w//4, top+h//3)
        ]
        pygame.draw.polygon(surface, (15, 35, 49), glass)
        pygame.draw.line(surface, (105, 175, 198), glass[0], glass[3], max(1, int(scale)))
        pygame.draw.line(surface, (105, 175, 198), glass[1], glass[2], max(1, int(scale)))
        lamp_w, lamp_h = max(2, w//8), max(2, h//9)
        pygame.draw.rect(surface, (255, 45, 35), (left+w//8, top+h//2, lamp_w, lamp_h))
        pygame.draw.rect(surface, (255, 45, 35), (left+w-w//8-lamp_w, top+h//2, lamp_w, lamp_h))
        pygame.draw.rect(surface, (28, 29, 34), (left+w//10, y-h//6, w*4//5, max(2,h//10)))
        pygame.draw.rect(surface, (235, 232, 215), (x-max(2,w//10), y-h//7, max(4,w//5), max(2,h//12)))
        highlight = tuple(max(0, min(255, channel+30)) for channel in self.color)
        pygame.draw.line(surface, highlight, (left+w//4, top+h//2), (left+w*3//4, top+h//2), max(1,int(scale)))
        
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
            self.speed += 42.0 * dt
            self.nitro = max(0.0, self.nitro - 26.0 * dt)
        else:
            self.nitro = min(100.0, self.nitro + 5.0 * dt)

        self.speed = clamp(self.speed, 0.0, PLAYER_MAX_SPEED + (45 if self.nitro_active else 0))
        steer = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.steering_direction = steer
        # The course pulls the rider outward through a bend; steering counters it.
        speed_ratio = self.speed / max(1.0, PLAYER_MAX_SPEED)
        steer_effectiveness = max(0.42, 1.0 - speed_ratio * 0.52)
        curve_drift = curve * speed_ratio * 0.28
        self.lane = clamp(self.lane + (steer * PLAYER_STEER * steer_effectiveness - curve_drift) * dt,
                          -MAX_LANE, MAX_LANE)
        self.hit_timer = max(0.0, self.hit_timer - dt)

    def _draw_car_player(self, surface, center_x):
        # Low, wide rear-view coupe with a short cabin, not a tall van profile.
        bottom = SCREEN_HEIGHT - 14
        w, h = 190, 78
        left, top = int(center_x - w/2), bottom-h
        pygame.draw.ellipse(surface, (25,35,30), (left+12,bottom-13,w-24,20))
        # Wide rear tires and wheel arches.
        pygame.draw.polygon(surface, (10,11,15), [(left+12,top+54),(left+42,top+49),(left+45,bottom-4),(left+17,bottom-4)])
        pygame.draw.polygon(surface, (10,11,15), [(left+w-42,top+49),(left+w-12,top+54),(left+w-17,bottom-4),(left+w-45,bottom-4)])
        body = (255,55,48) if self.hit_timer > 0 and int(self.hit_timer*16)%2 else (205,12,24)
        pygame.draw.polygon(surface,(65,7,14),[(left+9,top+39),(left+38,top+21),(left+71,top+11),(left+w-71,top+11),(left+w-38,top+21),(left+w-9,top+39),(left+w-2,bottom-18),(left+2,bottom-18)])
        pygame.draw.polygon(surface,body,[(left+18,top+40),(left+43,top+24),(left+75,top+15),(left+w-75,top+15),(left+w-43,top+24),(left+w-18,top+40),(left+w-15,bottom-25),(left+15,bottom-25)])
        # Broad sloping rear glass; roof is low and narrow.
        glass=[(left+77,top+16),(left+w-77,top+16),(left+w-57,top+37),(left+57,top+37)]
        pygame.draw.polygon(surface,(13,35,49),glass)
        pygame.draw.line(surface,(115,190,210),glass[0],glass[3],2)
        pygame.draw.line(surface,(115,190,210),glass[1],glass[2],2)
        pygame.draw.line(surface,(75,7,14),(left+31,top+43),(left+w-31,top+43),3)
        pygame.draw.rect(surface,(255,42,35),(left+20,top+48,40,10))
        pygame.draw.rect(surface,(255,42,35),(left+w-60,top+48,40,10))
        pygame.draw.rect(surface,(255,175,155),(left+25,top+51,27,3))
        pygame.draw.rect(surface,(255,175,155),(left+w-52,top+51,27,3))
        pygame.draw.rect(surface,(28,27,31),(left+13,bottom-25,w-26,10))
        pygame.draw.rect(surface,(235,232,215),(int(center_x-25),bottom-39,50,12))
        pygame.draw.rect(surface,(35,35,38),(int(center_x-20),bottom-36,40,6))
        pygame.draw.line(surface,(245,95,85),(left+25,top+41),(left+w-25,top+41),2)

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
    COLORS = [(35,95,235),(245,205,30),(35,185,80),(235,235,225),(190,55,185),(20,180,190),(150,235,35)]

    def __init__(self, index):
        super().__init__(random.choice(self.COLORS))
        self.index = index
        self.vehicle_type = "CAR"
        self.name = f"RIDER {index+1}"
        self.rider_color = self.COLORS[index % len(self.COLORS)]
        self.color = self.rider_color
        self.base_width = random.randint(92,112)
        self.base_height = random.randint(48,60)
        self.skill = random.uniform(0.88,1.12)
        self.aggression = random.uniform(0.35,0.95)
        self.change_timer = random.uniform(1.8,3.2)
        self.target_speed = random.uniform(155, 198) * self.skill
        self.stamina = 100.0
        self.stunned = 0.0
        self.finished = False

    def set_grid_position(self, player_progress, offset, lane):
        self.progress = max(0.0, player_progress + offset)
        self.lane = lane
        self.ai_lane_target = lane
        self.speed = 0.0
        self.finished = False

    def update_ai(self, player_progress, player_lane, player_speed, curve, dt, race_distance):
        if self.finished:
            return
        self.stunned = max(0.0, self.stunned-dt)
        self.change_timer -= dt

        # Each rival follows its own pace, acceleration and lane decisions.
        # A small, bounded catch-up adjustment keeps races close without mirroring
        # the player's speed or position.
        gap = self.progress - player_progress
        curve_load = min(1.0, abs(curve))
        # AI brakes for bends based on corner severity.
        corner_speed = 220.0 - curve_load * 105.0
        target_speed = min(self.target_speed, corner_speed)
        if gap < -420:
            target_speed += 7.0
        elif gap > 520:
            target_speed -= 5.0
        target_speed = clamp(target_speed, 125.0, 222.0)
        if self.stunned <= 0:
            acceleration = 15.0 if self.speed < target_speed else 0.0
            deceleration = (30.0 if curve_load > 0.45 else 10.0) if self.speed > target_speed else 0.0
            self.speed += (acceleration - deceleration) * dt
            self.speed = min(target_speed, self.speed)

        # Independent lane choices are made on a longer cadence. React only when
        # an actual nearby collision risk exists, rather than tracking the player.
        if self.change_timer <= 0:
            options = [-0.78, -0.39, 0.0, 0.39, 0.78]
            self.ai_lane_target = random.choice(options)
            self.change_timer = random.uniform(1.8, 4.2) / max(0.85, self.skill)
        if abs(gap) < 28 and abs(self.lane-player_lane) < 0.20:
            passing_lane = self.lane + random.choice([-0.48, 0.48])
            self.ai_lane_target = clamp(passing_lane, -0.82, 0.82)

        lane_response = min(1.0, dt * random.uniform(1.5, 2.2))
        self.lane += (self.ai_lane_target-self.lane) * lane_response
        self.lane = clamp(self.lane - curve*0.045*dt, -0.86, 0.86)
        self.progress += self.speed / 3.6 * dt
        if self.progress >= race_distance:
            self.progress = race_distance
            self.finished = True
