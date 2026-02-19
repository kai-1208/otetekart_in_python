import pygame as pg
import numpy as np
import time
from src.config import GameState, BUTTON_COLOR, BUTTON_HOVER_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from src.ui import Button
from src.renderer import new_frame
import math

class VSRace:
    def __init__(self, resources):
        self.resources = resources
        self.button_back = Button(400, 500, 400, 100, "Back to Course Select", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        # self.button_retry = Button(400, 400, 400, 100, "Retry", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR) # No retry in VS?
        self.hres = 120 
        self.harf_vres = 100
        self.mod = self.hres/60
        self.font = pg.font.Font("./fonts/cellar.ttf", 20)
        self.frame = np.zeros((self.hres, self.harf_vres*2, 3))
        self.delay = 1
        self.initialized = False
        self.paused = False
        
        self.button_back_waiting = Button(400, 500, 400, 80, "Back to Course Select", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        
        
        # Networking (Now using persistent instance from resources)
        self.is_ready = False
        self.joined_room = False
        
        self.reset()

    def reset(self):
        self.x_pos, self.y_pos, self.rot = 13, 2.5, np.pi
        self.velocity = 0
        self.lap_detection = False 
        self.lap_count = 0
        self.lap_times = []
        self.collision_check = False 
        
        current_course_imgs = self.resources.course_images[self.resources.current_course]
        
        self.cource = pg.surfarray.array3d(current_course_imgs["show"])
        self.sky = pg.surfarray.array3d(pg.transform.scale(current_course_imgs["sky"], (360, self.harf_vres*2)))
        
        self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
        if not self.initialized:
            self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
            self.initialized = True
            
        # Reset Network State (Clear old participants/rankings)
        self.resources.network.reset_state()
             
        self.lap_start_time = None
        self.is_ready = False
        self.local_finished = False
        self.joined_room = False

    def run(self, screen, events):
        # 1. Server State Polling (Required for conditions below)
        # 1. Server State Polling
        race_state, server_countdown, leaderboard = self.resources.network.get_gamestate()

        # 2. Join Room (Once)
        if not self.joined_room and self.resources.network.connected:
            self.resources.network.join_room(self.resources.current_course, self.resources.current_otete)
            self.joined_room = True

        # 3. ALWAYS send position (Fix asymmetry)
        if self.resources.network.connected:
            self.resources.network.send({
                "x": self.x_pos,
                "y": self.y_pos,
                "rot": self.rot,
                "otete_index": self.resources.current_otete,
                "course": self.resources.current_course
            })

        # 3. Unified Event Loop
        for event in events:
            if event.type == pg.QUIT:
                if self.resources.network.connected:
                     self.resources.network.leave_room()
                return "quit"
            
            if race_state == "WAITING":
                if self.button_back_waiting.is_clicked(event):
                    if self.resources.network.connected:
                        self.resources.network.leave_room()
                    return GameState.COURSE_SELECT
                # Ready on R key press (KEYDOWN for reliable detection)
                if event.type == pg.KEYDOWN and event.key == pg.K_r and not self.is_ready:
                    self.is_ready = True
                    self.resources.network.send({"type": "ready"})
                    print(f"[CLIENT] Sent ready status to server")

            if race_state == "FINISHED":
                if self.button_back.is_clicked(event):
                    if self.resources.network.connected:
                         self.resources.network.leave_room()
                    return GameState.COURSE_SELECT

        # 4. State Logic & Movement
        if race_state == "WAITING":
            if self.local_finished:
                 if self.resources.network.connected:
                      self.resources.network.leave_room()
                 return GameState.COURSE_SELECT
                
        elif race_state == "RACING":
            if self.lap_start_time is None:
                self.lap_start_time = time.time()
            self.x_pos, self.y_pos, self.rot, self.velocity = self.movement(self.x_pos, self.y_pos, self.rot, pg.key.get_pressed(), self.collision_check, self.velocity)

        # 5. DRAWING (WORLD) - Mode 7 Rendering
        self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
        surf = pg.surfarray.make_surface(self.frame * 255)
        screen.blit(pg.transform.scale(surf, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
        
        self.collision_detect(self.x_pos, self.y_pos, self.rot)
        self.render_others(screen)
        self.render(screen, pg.key.get_pressed())

        # 6. DRAWING (OVERLAYS)
        if race_state == "WAITING":
            # Semi-transparent overlay for text
            overlay = pg.Surface((400, 100))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 60))
            
            waiting_text = self.font.render(f"Waiting for players... (Room {self.resources.current_course})", True, (255, 255, 255))
            ready_text = self.font.render(f"Press 'R' to Ready! ({'READY' if self.is_ready else 'NOT READY'})", True, (0, 255, 0) if self.is_ready else (255, 0, 0))
            screen.blit(waiting_text, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 50))
            screen.blit(ready_text, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2))
            
            self.button_back_waiting.draw(screen)

        elif race_state == "COUNTDOWN":
            cnt_text = str(server_countdown) if server_countdown > 0 else "GO!"
            cnt_surf = self.font.render(cnt_text, True, (255, 0, 0))
            cnt_rect = cnt_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(cnt_surf, cnt_rect)

        elif race_state == "FINISHED":
            overlay = pg.Surface((500, 350))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (WINDOW_WIDTH//2 - 250, 30))
            
            title_text = self.font.render("RACE FINISHED!", True, (255, 215, 0))
            screen.blit(title_text, (WINDOW_WIDTH//2 - 80, 40))
            self.button_back.draw(screen) 

            # Draw Leaderboard with Characters
            start_y = 100
            for i, p in enumerate(leaderboard):
                pid = p.get('id')
                is_me = (pid == self.resources.network.client_id)
                
                otete_idx = p.get("otete_index", 0)
                char_img = self.resources.otete_images[otete_idx]["center"]
                char_img = pg.transform.scale(char_img, (40, 40))
                screen.blit(char_img, (150, start_y + i * 50 - 10))
                
                status = "FINISHED" if p['finished'] else "READY" if p.get('ready') else "WAITING"
                if p['finished']:
                    time_str = f"{p['time']:.2f}s"
                else:
                    time_str = f"Lap {p['lap']}"
                    
                label = f"{i+1}. {pid}"
                if is_me: label += " (YOU)"
                text = f"{label} - {status} ({time_str})"
                
                color = (0, 255, 0) if is_me else (255, 255, 255)
                line_surf = self.font.render(text, True, color)
                screen.blit(line_surf, (200, start_y + i * 50))

        if race_state == "RACING":
            for i, p in enumerate(leaderboard[:3]):
                t_str = f"{i+1}. Lap {p['lap']}"
                t_surf = self.font.render(t_str, True, (200, 200, 200))
                screen.blit(t_surf, (10, 50 + i*20))

        # 7. Debug HUD
        conn_status = "Connected" if self.resources.network.connected else "Disconnected"
        debug_text = f"{conn_status} | Mode: {race_state} | Others: {len(self.resources.network.get_others())}"
        debug_surf = self.font.render(debug_text, True, (255, 255, 0))
        screen.blit(debug_surf, (10, 10))

        return GameState.VS_RACE

    def render_others(self, screen):
        others = self.resources.network.get_others()
        # Note: Server handles room isolation. Any update received is for our room.
        for pid, data in others.items():
            if "x" not in data or "y" not in data:
                continue
                
            o_x, o_y = data["x"], data["y"]
            
            dx = o_x - self.x_pos
            dy = o_y - self.y_pos
            
            fwd_x = np.cos(self.rot)
            fwd_y = np.sin(self.rot)
            right_x = np.cos(self.rot + np.pi/2)
            right_y = np.sin(self.rot + np.pi/2)
            
            dist_fwd = dx * fwd_x + dy * fwd_y
            dist_right = dx * right_x + dy * right_y
            
            if dist_fwd > 0.1:
                scale_factor = 300 / dist_fwd 
                screen_x = 400 + (dist_right / dist_fwd) * 600
                screen_y = 300 + scale_factor * 0.5
                base_size = 50
                draw_size = max(10, int(base_size * scale_factor * 0.01))
                
                otete_idx = data.get("otete_index", 0)
                img = self.resources.otete_images[otete_idx]["center"]
                img = pg.transform.scale(img, (draw_size, draw_size))
                
                rect = img.get_rect(center=(int(screen_x), int(screen_y)))
                screen.blit(img, rect)

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

    def collision_detect(self, x_pos, y_pos, rot):
        """Collision detection only - rendering is handled by Mode 7"""
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
                    lap_end_time = time.time()
                    lap_time = lap_end_time - self.lap_start_time
                    self.lap_times.append(lap_time)
                    self.lap_start_time = lap_end_time
                    
                    if self.resources.network.connected:
                         self.resources.network.send({"type": "lap_update", "lap": self.lap_count})
                    
                    if self.lap_count == 3:
                        self.total_time = sum(self.lap_times)
                        self.local_finished = True
                        if self.resources.network.connected:
                             self.resources.network.send({"type": "finished", "time": self.total_time})

    def render(self, screen, keys):
        # Draw character sprite - centered at bottom like Time Attack
        sprite_type = "center"
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            sprite_type = "left"
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            sprite_type = "right"
        
        sprite = self.resources.otete_images[self.resources.current_otete][sprite_type]
        sprite = pg.transform.scale(sprite, (200, 200))
        screen.blit(sprite, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 180))

        # Lap times display
        for i, lap_time in enumerate(self.lap_times):            
            lap_text = self.font.render(f"Lap {i+1} : {lap_time:.2f}s", True, (255, 255, 255))
            screen.blit(lap_text, (WINDOW_WIDTH - 200, 40 + i * 25))
