import pygame as pg
import numpy as np
import time
from src.config import GameState, BUTTON_COLOR, BUTTON_HOVER_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from src.ui import Button
from src.renderer import new_frame
import math

class TimeAttack:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(400, 500, 400, 100, "Back to Start Screen", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.button2 = Button(400, 400, 400, 100, "Retry", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.hres = 120 # Horizontal resolution
        self.harf_vres = 100 # Half vertical resolution
        self.mod = self.hres/60
        self.font = pg.font.Font("./fonts/cellar.ttf", 20)
        self.frame = np.zeros((self.hres, self.harf_vres*2, 3))
        self.countdown_start_time = None
        self.countdown = 4
        self.delay = 1
        self.initialized = False
        self.paused = False
        self.pause_start_time = None 
        self.total_pause_time = 0 
        self.lap_pause_times = [] 
        self.joined_room = False
        
        self.reset()

    def reset(self):
        self.x_pos, self.y_pos, self.rot = 13, 2.5, np.pi
        self.velocity = 0
        self.lap_detection = False 
        self.lap_count = 0
        self.lap_times = []
        self.collision_check = False 
        
        # Access course images
        current_course_imgs = self.resources.course_images[self.resources.current_course]
        self.cource = pg.surfarray.array3d(current_course_imgs["show"])
        self.sky = pg.surfarray.array3d(pg.transform.scale(current_course_imgs["sky"], (360, self.harf_vres*2)))
        
        # Initial frame generation
        self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
        if not self.initialized:
            self.initialized = True
            
        # Reset network state for a clean start
        self.resources.network.reset_state()
        self.joined_room = False
             
        self.lap_start_time = None
        self.countdown_start_time = time.time()
        self.paused = False
        self.pause_start_time = None
        self.total_pause_time = 0
        self.lap_pause_times = [0] * 3

    def run(self, screen, events):
        # 1. Join Room (Once/Robust)
        if not self.joined_room and self.resources.network.connected:
            # Use Course + 10 for Time Attack room isolation
            self.resources.network.join_room(self.resources.current_course + 10, self.resources.current_otete)
            self.joined_room = True

        # 2. Always Send Position (ASync Fix)
        if self.resources.network.connected:
            self.resources.network.send({
                "x": self.x_pos,
                "y": self.y_pos,
                "rot": self.rot,
                "otete_index": self.resources.current_otete,
                "course": self.resources.current_course
            })

        # 3. Event Loop
        for event in events:
            if event.type == pg.QUIT:
                if self.resources.network.connected:
                     self.resources.network.leave_room()
                return "quit"
            
            if self.paused:
                if self.button1.is_clicked(event):
                    if self.resources.network.connected:
                         self.resources.network.leave_room()
                    return GameState.COURSE_SELECT
                if self.button2.is_clicked(event):
                    self.reset()
                    self.paused = False
                    return GameState.TIME_ATTACK
            elif self.lap_count >= 3:
                if self.button1.is_clicked(event):
                    if self.resources.network.connected:
                         self.resources.network.leave_room()
                    return GameState.COURSE_SELECT
                if self.button2.is_clicked(event):
                    self.reset()
                    return GameState.TIME_ATTACK
            
            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                self.paused = not self.paused
                if self.paused:
                    self.pause_start_time = time.time()
                else:
                    pause_time = time.time() - self.pause_start_time
                    self.total_pause_time += pause_time
                    if self.lap_count < len(self.lap_pause_times):
                        self.lap_pause_times[self.lap_count] += pause_time

        # 4. Movement Logic (Blocked by pause or countdown)
        elapsed_time = time.time() - self.countdown_start_time - self.total_pause_time
        in_countdown = elapsed_time < (self.delay + self.countdown + 1)
        
        if not self.paused and not in_countdown and self.lap_count < 3:
            if self.lap_start_time is None:
                self.lap_start_time = time.time()
            self.x_pos, self.y_pos, self.rot, self.velocity = self.movement(self.x_pos, self.y_pos, self.rot, pg.key.get_pressed(), self.collision_check, self.velocity)

        # 5. Drawing (World) - Always visible
        self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
        surf = pg.surfarray.make_surface(self.frame*255)
        screen.blit(pg.transform.scale(surf, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
        
        self.collision(self.x_pos, self.y_pos, self.rot, screen) 
        self.render_others(screen)
        self.render(screen, pg.key.get_pressed())

        # 6. Drawing (Overlays)
        if self.paused:
            overlay = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            pause_text = self.font.render("PAUSED", True, (255, 255, 255))
            screen.blit(pause_text, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 100))
            self.button1.draw(screen)
            self.button2.draw(screen)
        
        elif in_countdown:
            if elapsed_time > self.delay:
                cd_elapsed = elapsed_time - self.delay
                countdown_value = self.countdown - int(cd_elapsed)
                if countdown_value > 0:
                    cd_text = str(countdown_value)
                else:
                    cd_text = "GO!"
                cd_surf = self.font.render(cd_text, True, (255, 255, 0))
                cd_rect = cd_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                screen.blit(cd_surf, cd_rect)
        
        elif self.lap_count >= 3:
            # Finish screen overlay
            overlay = pg.Surface((500, 300))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (WINDOW_WIDTH//2 - 250, 50))
            
            title_text = self.font.render("RACE FINISHED!", True, (255, 215, 0))
            screen.blit(title_text, (WINDOW_WIDTH//2 - 80, 60))
            
            total_time = sum(self.lap_times)
            total_text = self.font.render(f"Total Time: {total_time:.2f}s", True, (255, 255, 255))
            screen.blit(total_text, (WINDOW_WIDTH//2 - 80, 100))
            
            for i, t in enumerate(self.lap_times):
                lap_text = self.font.render(f"Lap {i+1}: {t:.2f}s", True, (200, 200, 200))
                screen.blit(lap_text, (WINDOW_WIDTH//2 - 60, 140 + i * 25))
            

            
            self.button1.draw(screen)
            self.button2.draw(screen)

        # 7. Debug HUD
        conn_status = "Connected" if self.resources.network.connected else "Disconnected"
        others_count = len(self.resources.network.get_others())
        debug_text = f"{conn_status} | ID: {self.resources.network.client_id} | Others: {others_count}"
        debug_surf = self.font.render(debug_text, True, (255, 255, 0))
        screen.blit(debug_surf, (10, 10))

        return GameState.TIME_ATTACK

    def render_others(self, screen):
        others = self.resources.network.get_others()
        for pid, data in others.items():
            if "x" not in data or "y" not in data:
                continue
                
            o_x, o_y = data["x"], data["y"]
            o_rot = data.get("rot", 0)
            o_otete_idx = data.get("otete_index", 0)
            
            # Distance and angle to other
            dx = o_x - self.x_pos
            dy = o_y - self.y_pos
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 15: continue
            
            angle_to_other = math.atan2(dy, dx)
            rel_angle = angle_to_other - self.rot
            while rel_angle > math.pi: rel_angle -= 2*math.pi
            while rel_angle < -math.pi: rel_angle += 2*math.pi
            
            if abs(rel_angle) < math.pi/3:
                # Ghost rendering logic
                screen_x = WINDOW_WIDTH // 2 + math.tan(rel_angle) * (WINDOW_WIDTH // 2)
                size = min(200, max(40, 250 / (1 + dist * 0.3)))  # Max same as player (200)
                
                # Determine sprite based on relative rotation
                rel_rot = o_rot - angle_to_other
                while rel_rot > math.pi: rel_rot -= 2*math.pi
                while rel_rot < -math.pi: rel_rot += 2*math.pi
                
                sprite_type = "center"
                if rel_rot < -math.pi/4: sprite_type = "right"
                elif rel_rot > math.pi/4: sprite_type = "left"
                
                sprite = self.resources.otete_images[o_otete_idx][sprite_type]
                sprite = pg.transform.scale(sprite, (int(size), int(size)))
                sprite.set_alpha(150) # Ghostly transparency
                
                rect = sprite.get_rect(center=(int(screen_x), int(WINDOW_HEIGHT//2 - 0 + 60/(dist+0.3))))
                screen.blit(sprite, rect)

    def collision_check(self, x, y):
        try:
            if x < 0 or x >= self.cource.shape[0] or y < 0 or y >= self.cource.shape[1]:
                return False
            pixel_color = self.cource[int(x), int(y)]
            # Check for black (off-track)
            if (pixel_color == [0, 0, 0]).all():
                return False
            return True
        except:
            return False

    def movement(self, x_pos, y_pos, rot, keys, collision_check, velocity):
        if self.lap_count == 3:
            return x_pos, y_pos, rot, velocity

        otete = self.resources.character_parameter[self.resources.current_otete]

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            rot -= 0.008 * otete.handling
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            rot += 0.008 * otete.handling
        if keys[pg.K_UP] or keys[pg.K_w]:
            if collision_check == False: 
                if velocity < 0.015 * otete.speed:
                    velocity += 0.0007 * otete.acceleration
                x_pos += velocity*np.cos(rot)
                y_pos += velocity*np.sin(rot)
            elif collision_check == True: 
                velocity = -0.05
                x_pos += velocity*np.cos(rot)
                y_pos += velocity*np.sin(rot)
            elif collision_check == "Dirt": 
                velocity = 0.006 * otete.speed
                x_pos += velocity*np.cos(rot)
                y_pos += velocity*np.sin(rot)
        else:
            if velocity > 0:
                velocity -= 0.001
            if velocity < 0.005:
                velocity = 0
            x_pos += velocity*np.cos(rot)
            y_pos += velocity*np.sin(rot)

        return x_pos, y_pos, rot, velocity

    def collision_check_internal(self, x, y):
        try:
            if x < 0 or x >= self.cource.shape[0] or y < 0 or y >= self.cource.shape[1]:
                return False
            pixel_color = self.cource[int(x), int(y)]
            if (pixel_color == [0, 0, 0]).all():
                return False
            return True
        except:
            return False

    def collision(self, x_pos, y_pos, rot, screen):
        """Collision detection with track physics"""
        player_x, player_y = int(x_pos * 10), int(y_pos * 10)
        cource_array = pg.surfarray.array3d(self.resources.course_images[self.resources.current_course]["collision"])

        if 0 <= player_x < cource_array.shape[0] and 0 <= player_y < cource_array.shape[1]:
            pixel_color = cource_array[player_x, player_y]

            if (pixel_color == [0, 0, 0]).all():
                self.collision_check = True
            elif (pixel_color == [255, 255, 255]).all():
                self.collision_check = False
            elif (pixel_color == [127, 0, 0]).all():
                self.collision_check = "Dirt"
            elif (pixel_color == [255, 255, 0]).all():
                self.lap_detection = True
            elif (pixel_color == [255, 0, 0]).all():
                if self.lap_detection == True:
                    self.lap_count += 1
                    self.lap_detection = False
                    if self.lap_start_time:
                        self.lap_times.append(time.time() - self.lap_start_time)
                    self.lap_start_time = time.time()
                    
                    if self.lap_count == 3:
                        if self.resources.network.connected:
                            self.resources.network.send({"type": "finished", "time": sum(self.lap_times)})

    def render(self, screen, keys):
        # Draw character sprite
        sprite_type = "center"
        if keys[pg.K_LEFT]: sprite_type = "left"
        if keys[pg.K_RIGHT]: sprite_type = "right"
        
        sprite = self.resources.otete_images[self.resources.current_otete][sprite_type]
        sprite = pg.transform.scale(sprite, (200, 200))
        screen.blit(sprite, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 180))
        
        # Lap Info
        lap_text = self.font.render(f"Lap: {min(self.lap_count+1, 3)}/3", True, (255, 255, 255))
        screen.blit(lap_text, (WINDOW_WIDTH - 200, 20))
        
        for i, t in enumerate(self.lap_times):
            t_surf = self.font.render(f"Lap {i+1}: {t:.2f}s", True, (200, 200, 200))
            screen.blit(t_surf, (WINDOW_WIDTH - 200, 50 + i*20))
