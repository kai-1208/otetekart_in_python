import pygame as pg
import numpy as np
import time
from numba import njit

pg.init() # 初期化
window_size = (800, 600)
screen = pg.display.set_mode(window_size)
clock = pg.time.Clock()
# pg.display.set_caption("otete kart")

# ゲームの状態管理
class GameState:
    start_screen = "startScreen"
    character_select = "characterSelect"
    cource_select = "courceSelect"
    time_attack = "timeAttack"
    how_to_play = "howToPlay"
    credit_screen = "creditScreen"

class CharacterParameter:
    def __init__(self, name, speed, acceleration, handling):
        self.name = name
        self.speed = speed
        self.acceleration = acceleration
        self.handling = handling

# リソース管理
class Resource:
    def __init__(self):
        self.start_screen_bg = pg.image.load("./img/start_screen_bg.png")
        self.start_screen_bg = pg.transform.scale(self.start_screen_bg, (self.start_screen_bg.get_width() * 5, self.start_screen_bg.get_height() * 5))
        self.character_select_bg = pg.image.load("./img/character_select_bg.png")
        self.character_select_bg = pg.transform.scale(self.character_select_bg, (self.character_select_bg.get_width() * 5, self.character_select_bg.get_height() * 5))

        self.font = pg.font.Font("./fonts/cellar.ttf", 20)

        arrow_scale = 2
        self.right_arrow = pg.image.load("./img/right_arrow.png")
        self.right_arrow = pg.transform.scale(self.right_arrow, (self.right_arrow.get_width() * arrow_scale, self.right_arrow.get_height() * arrow_scale))
        self.left_arrow = pg.transform.flip(self.right_arrow, True, False)

        self.otete_images = {}
        otete_scale = 4
        for i in range(4):
            otete = pg.image.load(f"./img/otetekart{i+1}.png")
            self.otete_images[i] = {
                "select": pg.transform.scale(otete.subsurface(pg.Rect(0, 0, 50, 50)), (otete.subsurface(pg.Rect(0, 0, 50, 50)).get_width() * otete_scale, otete.subsurface(pg.Rect(0, 0, 50, 50)).get_height() * otete_scale)),
                "left": pg.transform.scale(otete.subsurface(pg.Rect(50, 0, 50, 50)), (otete.subsurface(pg.Rect(50, 0, 50, 50)).get_width() * otete_scale, otete.subsurface(pg.Rect(50, 0, 50, 50)).get_height() * otete_scale)),
                "center": pg.transform.scale(otete.subsurface(pg.Rect(100, 0, 50, 50)), (otete.subsurface(pg.Rect(100, 0, 50, 50)).get_width() * otete_scale, otete.subsurface(pg.Rect(100, 0, 50, 50)).get_height() * otete_scale)),
                "right": pg.transform.scale(otete.subsurface(pg.Rect(150, 0, 50, 50)), (otete.subsurface(pg.Rect(150, 0, 50, 50)).get_width() * otete_scale, otete.subsurface(pg.Rect(150, 0, 50, 50)).get_height() * otete_scale)),
            }
        self.cource_images = {}
        for i in range(4):
            cource = pg.image.load(f"./img/cource{i+1}.png")
            self.cource_images[i] = {
                "collision": cource.subsurface(pg.Rect(0, 0, 200, 200)),
                "show": cource.subsurface(pg.Rect(200, 0, 200, 200)),
                "sky": cource.subsurface(pg.Rect(400, 0, 200, 50)),
            }
        self.player = pg.image.load("./img/player.png")
        # player_scale = 10
        # self.player = pg.transform.scale(self.player, (self.player.get_width() * player_scale, self.player.get_height() * player_scale))
        self.current_otete = 0
        self.current_cource = 0

        self.character_parameter = [
            CharacterParameter("otete1", 2, 5, 4),
            CharacterParameter("otete2", 3, 4, 4),
            CharacterParameter("otete3", 4, 3, 2),
            CharacterParameter("otete4", 5, 2, 1),
        ]

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color

    def draw(self, screen):
        mouse_pos = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pg.draw.rect(screen, self.hover_color, self.rect)
        else:
            pg.draw.rect(screen, self.color, self.rect)

        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: # 左クリックを検知
            if self.rect.collidepoint(event.pos): # ボタンの範囲内をクリックされたか
                return True
        return False

# スタート画面
class StartScrean:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(400, 300, 400, 100, "Time Attack", self.resources.font, (26, 175, 0), (76, 225, 50))
        self.button2 = Button(400, 400, 400, 100, "How to Play", self.resources.font, (26, 175, 0), (76, 225, 50))
        self.button3 = Button(400, 500, 400, 100, "Credit", self.resources.font, (26, 175, 0), (76, 225, 50))

    def run(self, screen, events):
        screen.blit(self.resources.start_screen_bg, (0, 0))
        self.button1.draw(screen)
        self.button2.draw(screen)
        self.button3.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if self.button1.is_clicked(event):
                return GameState.character_select
            if self.button2.is_clicked(event):
                return GameState.how_to_play
            if self.button3.is_clicked(event):
                return GameState.credit_screen
        return GameState.start_screen


# キャラクター選択画面
class CharacterSelect:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(0, 500, 400, 100, "Back to Start Screen", self.resources.font, (26, 175, 0), (76, 225, 50))
        self.button2 = Button(400, 500, 400, 100, "Go to Cource Select", self.resources.font, (26, 175, 0), (76, 225, 50))

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))
        screen.blit(self.resources.otete_images[self.resources.current_otete]["select"], (300, 200))
        screen.blit(self.resources.left_arrow, (200, 300))
        screen.blit(self.resources.right_arrow, (500, 300))
        self.button1.draw(screen)
        self.button2.draw(screen)

        chracter_name = self.resources.character_parameter[self.resources.current_otete].name
        speed = self.resources.character_parameter[self.resources.current_otete].speed
        acceleration = self.resources.character_parameter[self.resources.current_otete].acceleration
        handling = self.resources.character_parameter[self.resources.current_otete].handling
        chracter_name_text = self.resources.font.render(f"Name : {chracter_name}", True, (255, 255, 255))
        parameter_text = self.resources.font.render(f"Speed : {speed}, Acceleration : {acceleration}, Handling : {handling}", True, (255, 255, 255))
        screen.blit(chracter_name_text, (50, 50))
        screen.blit(parameter_text, (50, 100))

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if pg.Rect(200, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_otete = (self.resources.current_otete - 1) % 4
                if pg.Rect(500, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_otete = (self.resources.current_otete + 1) % 4
            if self.button1.is_clicked(event):
                return GameState.start_screen
            if self.button2.is_clicked(event):
                return GameState.cource_select
        return GameState.character_select

# コース選択画面
class CourceSelect:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(0, 500, 400, 100, "Back to Character Select", self.resources.font, (26, 175, 0), (76, 225, 50))
        self.button2 = Button(400, 500, 400, 100, "Go to Time Attack", self.resources.font, (26, 175, 0), (76, 225, 50))

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))
        screen.blit(self.resources.cource_images[self.resources.current_cource]["show"], (300, 200))
        screen.blit(self.resources.left_arrow, (200, 300))
        screen.blit(self.resources.right_arrow, (500, 300))
        self.button1.draw(screen)
        self.button2.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if pg.Rect(200, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_cource = (self.resources.current_cource - 1) % 4
                if pg.Rect(500, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_cource = (self.resources.current_cource + 1) % 4
            if self.button1.is_clicked(event):
                return GameState.character_select
            if self.button2.is_clicked(event):
                return GameState.time_attack
        return GameState.cource_select

# タイムアタック画面
class TimeAttack:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(400, 500, 400, 100, "Back to Start Screen", self.resources.font, (26, 175, 0), (76, 225, 50))
        self.button2 = Button(400, 400, 400, 100, "Retry", self.resources.font, (26, 175, 0), (76, 225, 50))
        self.hres = 120 # 水平解像度
        self.harf_vres = 100 # 垂直解像度の半分
        self.mod = self.hres/60
        self.font = pg.font.Font("./fonts/cellar.ttf", 20)
        self.frame = np.zeros((self.hres, self.harf_vres*2, 3))
        self.countdown_start_time = None
        self.countdown = 4
        self.delay = 1
        self.initialized = False
        self.paused = False
        self.pause_start_time = None # ポーズ開始時間
        self.total_pause_time = 0 # ポーズの合計時間
        self.lap_pause_times = [] # ラップのポーズ時間
        self.reset()

    def reset(self):
        self.x_pos, self.y_pos, self.rot = 13, 2.5, np.pi
        self.velocity = 0
        self.lap_detection = False # 周回判定
        self.lap_count = 0
        self.lap_times = []
        self.collision_check = False # 当たり判定
        self.cource = pg.surfarray.array3d(self.resources.cource_images[self.resources.current_cource]["show"])
        self.sky = pg.surfarray.array3d(pg.transform.scale(self.resources.cource_images[self.resources.current_cource]["sky"], (360, self.harf_vres*2)))
        self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
        if not self.initialized:
            self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
            self.initialized = True
        self.lap_start_time = None
        self.countdown_start_time = time.time()
        self.paused = False
        self.pause_start_time = None
        self.total_pause_time = 0
        self.lap_pause_times = [0] * 3

    def run(self, screen, events):
        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if self.button1.is_clicked(event):
                self.reset()
                return GameState.start_screen
            if self.button2.is_clicked(event):
                self.reset()
                self.paused = False
                return GameState.time_attack
            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                self.paused = not self.paused
                if self.paused:
                    self.pause_start_time = time.time()
                else:
                    pause_time = time.time() - self.pause_start_time
                    self.total_pause_time += time.time() - self.pause_start_time
                    if self.lap_count < len(self.lap_pause_times):
                        self.lap_pause_times[self.lap_count] += pause_time

        if self.paused:
            screen.blit(self.font.render("Paused", True, (255, 255, 255)), (400, 300))
            self.button1.draw(screen)
            self.button2.draw(screen)
            pg.display.flip()
            return GameState.time_attack

        # カウントダウンの前にディレイ
        elapsed_time = time.time() - self.countdown_start_time - self.total_pause_time
        if elapsed_time < self.delay:
            screen.blit(pg.transform.scale(pg.surfarray.make_surface(self.frame * 255), (800, 600)), (0, 0))
            pg.display.flip()
            return GameState.time_attack
        
        # カウントダウン
        elapsed_time = time.time() - self.countdown_start_time - self.total_pause_time
        if elapsed_time < self.countdown + 1:
            countdown_value = self.countdown - int(elapsed_time)
            if countdown_value > 0:
                countdown_text = str(countdown_value)
            else:
                countdown_text = "Go!"
            countdown_text_surface = self.font.render(countdown_text, True, (255, 255, 255))
            screen.blit(pg.transform.scale(pg.surfarray.make_surface(self.frame * 255), (800, 600)), (0, 0))
            screen.blit(countdown_text_surface, (400, 300))
            pg.display.flip()
            return GameState.time_attack
        
        if self.lap_start_time is None:
            self.lap_start_time = time.time()
        
        self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
        surf = pg.surfarray.make_surface(self.frame*255)
        surf = pg.transform.scale(surf, (800, 600))
        screen.blit(surf, (0, 0))
        self.x_pos, self.y_pos, self.rot, self.velocity = self.movement(self.x_pos, self.y_pos, self.rot, pg.key.get_pressed(), self.collision_check, self.velocity)
        self.collision(self.x_pos, self.y_pos, self.rot)
        self.render(screen, pg.key.get_pressed())

        return GameState.time_attack

    def movement(self, x_pos, y_pos, rot, keys, collision_check, velocity):
        if self.lap_count == 3:
            return x_pos, y_pos, rot, velocity

        otete = self.resources.character_parameter[self.resources.current_otete]

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            rot -= 0.008 * otete.handling
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            rot += 0.008 * otete.handling
        if keys[pg.K_UP] or keys[pg.K_w]:
            if collision_check == False: # 0.05
                if velocity < 0.015 * otete.speed:
                    velocity += 0.0007 * otete.acceleration
                x_pos += velocity*np.cos(rot)
                y_pos += velocity*np.sin(rot)
            elif collision_check == True: # 0.1
                velocity = -0.05
                x_pos += velocity*np.cos(rot)
                y_pos += velocity*np.sin(rot)
            elif collision_check == "Dirt": # 0.02
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

    def collision(self, x_pos, y_pos, rot):
        player_x, player_y = int(x_pos * 10), int(y_pos * 10)
        cource_array = pg.surfarray.array3d(self.resources.cource_images[self.resources.current_cource]["collision"])

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
                    if self.lap_count <= len(self.lap_pause_times):
                        lap_time = lap_end_time - self.lap_start_time - self.lap_pause_times[self.lap_count - 1]
                    else:
                        lap_time = lap_end_time - self.lap_start_time
                    self.lap_times.append(lap_time)
                    self.lap_start_time = lap_end_time
                    if self.lap_count == 3:
                        self.total_time = sum(self.lap_times)

        screen.blit(self.resources.cource_images[self.resources.current_cource]["show"], (0, 0))
        screen.blit(self.resources.player, (x_pos * 10, y_pos * 10))

    def render(self, screen, keys):
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            screen.blit(self.resources.otete_images[self.resources.current_otete]["left"], (300, 450))
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            screen.blit(self.resources.otete_images[self.resources.current_otete]["right"], (300, 450))
        else:
            screen.blit(self.resources.otete_images[self.resources.current_otete]["center"], (300, 450))

        for i, lap_time in enumerate(self.lap_times):            
            lap_text = self.font.render(f"Lap {i+1} : {lap_time:.2f} seconds", True, (255, 255, 255))
            screen.blit(lap_text, (400, 10 + i * 30))

        if self.lap_count == 3:
            total_time_text = self.font.render(f"Total time : {self.total_time:.2f} seconds", True, (255, 255, 255))
            screen.blit(total_time_text, (400, 10 + len(self.lap_times) * 30))
            thank_you_text = self.font.render("Thank you for playing!", True, (255, 255, 255))
            screen.blit(thank_you_text, (400, 10 + (len(self.lap_times) + 1) * 30))
            self.button1.draw(screen)

@njit # fps上げるためにnumbaで高速化
def new_frame(x_pos, y_pos, rot, hres, harf_vres, mod, sky, cource, frame):
    for i in range(hres):
        i_rot = rot + np.deg2rad(i/mod-30)
        sin, cos = np.sin(i_rot), np.cos(i_rot)
        cos2 = np.cos(np.deg2rad(i/mod-30))
        index = int(np.rad2deg(i_rot)%360)
        if index >= 360:
            index = 359
        frame[i][:] = sky[index][:]/255

        for j in range(harf_vres):
            n = (harf_vres/(harf_vres-j))/cos2
            x, y = x_pos + n*cos, y_pos + n*sin
            xx, yy = int(x/20%1*200), int(y/20%1*200)
            frame[i][harf_vres*2-j-1] = cource[xx][yy]/255

    return frame

# 操作説明画面
class HowToPlayScreen:
    def __init__(self, resources):
        self.resources = resources
        self.font = self.resources.font
        self.button = Button(400, 500, 400, 100, "Back to Start Screen", self.font, (26, 175, 0), (76, 225, 50))

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))
        self.button.draw(screen)

        key_bindings_text1 = self.font.render("Key Bindings :", True, (255, 255, 255))
        screen.blit(key_bindings_text1, (50, 100))
        key_bindings_text2 = self.font.render("W key / Up Arrow : Accelerate", True, (255, 255, 255))
        screen.blit(key_bindings_text2, (50, 150))
        key_bindings_text3 = self.font.render("A key / Left Arrow : Turn Left", True, (255, 255, 255))
        screen.blit(key_bindings_text3, (50, 200))
        key_bindings_text4 = self.font.render("D key / Right Arrow : Turn Right", True, (255, 255, 255))
        screen.blit(key_bindings_text4, (50, 250))
        key_bindings_text5 = self.font.render("P key : Pause", True, (255, 255, 255))
        screen.blit(key_bindings_text5, (50, 300))

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if self.button.is_clicked(event):
                return GameState.start_screen
        return GameState.how_to_play

# クレジット画面    
class CreditScreen:
    def __init__(self, resources):
        self.resources = resources
        self.font = self.resources.font
        self.button = Button(400, 500, 400, 100, "Back to Start Screen", self.font, (26, 175, 0), (76, 225, 50))

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))
        self.button.draw(screen)

        credit_text1 = self.font.render("Creator : kai-1208", True, (255, 255, 255))
        screen.blit(credit_text1, (50, 100))
        credit_text2 = self.font.render("Graphics : kai-1208", True, (255, 255, 255))
        screen.blit(credit_text2, (50, 150))
        credit_text3 = self.font.render("Music : ", True, (255, 255, 255))
        screen.blit(credit_text3, (50, 200))
        credit_text4 = self.font.render("Sound Effect : ", True, (255, 255, 255))
        screen.blit(credit_text4, (50, 250))
        credit_text5 = self.font.render("Font (Cellar) : Dan", True, (255, 255, 255))
        screen.blit(credit_text5, (50, 300))

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if self.button.is_clicked(event):
                return GameState.start_screen
        return GameState.credit_screen

# メインループ
def main():
    resources = Resource()
    state = GameState.start_screen
    screens = {
        GameState.start_screen: StartScrean(resources),
        GameState.character_select: CharacterSelect(resources),
        GameState.cource_select: CourceSelect(resources),
        GameState.time_attack: TimeAttack(resources),
        GameState.how_to_play: HowToPlayScreen(resources),
        GameState.credit_screen: CreditScreen(resources),
    }
    running = True
    while running:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False

        # ゲームの状態に応じて画面を描画
        if state in screens:
            new_state = screens[state].run(screen, events)
            if new_state == "quit":
                running = False
            else:
                state = new_state

        pg.display.update() # 画面を更新
        clock.tick(60) # 60FPSに設定
        pg.display.set_caption(f"otete kart FPS: {int(clock.get_fps())}")

    pg.quit()

if __name__ == "__main__":
    main()