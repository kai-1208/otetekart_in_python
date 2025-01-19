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
    result_screen = "resultScreen"
    credit_screen = "creditScreen"

# リソース管理
class Resource:
    def __init__(self):
        self.start_screen_bg = pg.image.load("./img/start_screen_bg.png")
        self.start_screen_bg = pg.transform.scale(self.start_screen_bg, (self.start_screen_bg.get_width() * 5, self.start_screen_bg.get_height() * 5))
        self.character_select_bg = pg.image.load("./img/character_select_bg.png")
        self.character_select_bg = pg.transform.scale(self.character_select_bg, (self.character_select_bg.get_width() * 5, self.character_select_bg.get_height() * 5))
        self.cource_select_bg = pg.image.load("./img/character_select_bg.png")
        self.cource_select_bg = pg.transform.scale(self.cource_select_bg, (self.cource_select_bg.get_width() * 5, self.cource_select_bg.get_height() * 5))

        font_path = "./fonts/enter-the-gungeon-big.ttf"
        font_size = 30
        font = pg.font.Font(font_path, font_size)

        # (x, y, width, height, text, font, color, hover_color)
        self.character_select_button = Button(500, 300, 300, 100, "Time Attack", font, (26, 175, 0), (255, 255, 255))
        self.credit_button = Button(500, 400, 300, 100, "Credit", font, (26, 175, 0), (255, 255, 255))
        self.cource_select_button = Button(500, 500, 300, 100, "Cource Select", font, (26, 175, 0), (255, 255, 255))
        self.time_attack_button = Button(500, 500, 300, 100, "Time Attack", font, (26, 175, 0), (255, 255, 255))

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
        player_scale = 10
        self.player = pg.transform.scale(self.player, (self.player.get_width() * player_scale, self.player.get_height() * player_scale))

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

        text_surface = self.font.render(self.text, True, (0, 0, 0))
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

    def run(self, screen, events):
        screen.blit(self.resources.start_screen_bg, (0, 0))

        self.resources.character_select_button.draw(screen)
        self.resources.credit_button.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if self.resources.character_select_button.is_clicked(event):
                return GameState.character_select
            if self.resources.credit_button.is_clicked(event):
                return GameState.credit_screen
        return GameState.start_screen


# キャラクター選択画面
class CharacterSelect:
    def __init__(self, resources):
        self.resources = resources
        self.current_otete = 1

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))

        screen.blit(self.resources.otete_images[self.current_otete]["select"], (300, 200))

        screen.blit(self.resources.left_arrow, (200, 300))
        screen.blit(self.resources.right_arrow, (500, 300))

        self.resources.cource_select_button.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if pg.Rect(200, 300, 100, 100).collidepoint(event.pos):
                    self.current_otete = (self.current_otete - 1) % 4
                if pg.Rect(500, 300, 100, 100).collidepoint(event.pos):
                    self.current_otete = (self.current_otete + 1) % 4
            if self.resources.cource_select_button.is_clicked(event):
                return GameState.cource_select
        return GameState.character_select

# コース選択画面
class CourceSelect:
    def __init__(self, resources):
        self.resources = resources
        self.current_cource = 0

    def run(self, screen, events):
        screen.blit(self.resources.cource_select_bg, (0, 0))

        screen.blit(self.resources.cource_images[self.current_cource]["show"], (300, 200))

        screen.blit(self.resources.left_arrow, (200, 300))
        screen.blit(self.resources.right_arrow, (500, 300))

        self.resources.time_attack_button.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if pg.Rect(200, 300, 100, 100).collidepoint(event.pos):
                    self.current_cource = (self.current_cource - 1) % 4
                if pg.Rect(500, 300, 100, 100).collidepoint(event.pos):
                    self.current_cource = (self.current_cource + 1) % 4
            if self.resources.time_attack_button.is_clicked(event):
                return GameState.time_attack
        return GameState.cource_select

# タイムアタック画面
class TimeAttack:
    def __init__(self, resources):
        self.resources = resources
        self.hres = 120 # 水平解像度
        self.harf_vres = 100 # 垂直解像度の半分
        self.mod = self.hres/60
        self.x_pos, self.y_pos, self.rot = 13, 2.5, np.pi
        self.velocity = 0
        self.frame = np.random.uniform(0, 1, (self.hres, self.harf_vres*2, 3))
        self.cource = pg.surfarray.array3d(self.resources.cource_images[0]["show"])
        self.sky = pg.surfarray.array3d(pg.transform.scale(self.resources.cource_images[1]["sky"], (360, self.harf_vres*2)))
        self.collision_check = False

    def run(self, screen, events):
        for event in events:
            if event.type == pg.QUIT:
                return "quit"

        self.frame = new_frame(self.x_pos, self.y_pos, self.rot, self.hres, self.harf_vres, self.mod, self.sky, self.cource, self.frame)
        surf = pg.surfarray.make_surface(self.frame*255)
        surf = pg.transform.scale(surf, (800, 600))
        screen.blit(surf, (0, 0))
        self.x_pos, self.y_pos, self.rot, self.velocity = self.movement(self.x_pos, self.y_pos, self.rot, pg.key.get_pressed(), self.collision_check, self.velocity)
        self.collision(self.x_pos, self.y_pos, self.rot)
        self.render(screen, pg.key.get_pressed())

        return GameState.time_attack

    def movement(self, x_pos, y_pos, rot, keys, collision_check, velocity):
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            rot -= 0.03
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            rot += 0.03
        if keys[pg.K_UP] or keys[pg.K_w]:
            if collision_check == False: # 0.05
                if velocity < 0.05:
                    velocity += 0.001
                x_pos += velocity*np.cos(rot)
                y_pos += velocity*np.sin(rot)
            elif collision_check == True: # 0.1
                velocity = -0.05
                x_pos += velocity*np.cos(rot)
                y_pos += velocity*np.sin(rot)
            elif collision_check == "Dirt": # 0.02
                velocity = 0.02
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
        cource_array = pg.surfarray.array3d(self.resources.cource_images[0]["collision"])

        if 0 <= player_x < cource_array.shape[0] and 0 <= player_y < cource_array.shape[1]:
            pixel_color = cource_array[player_x, player_y]

            if (pixel_color == [0, 0, 0]).all():
                self.collision_check = True
            elif (pixel_color == [255, 255, 255]).all():
                self.collision_check = False
            elif (pixel_color == [127, 0, 0]).all():
                self.collision_check = "Dirt"

        screen.blit(self.resources.cource_images[0]["collision"], (0, 0))
        screen.blit(self.resources.player, (x_pos * 10, y_pos * 10))

    def render(self, screen, keys):
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            screen.blit(self.resources.otete_images[0]["left"], (300, 450))
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            screen.blit(self.resources.otete_images[0]["right"], (300, 450))
        else:
            screen.blit(self.resources.otete_images[0]["center"], (300, 450))

@njit
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

# リザルト画面
class ResultScreen:
    def __init__(self):
        pass

# クレジット画面    
class CreditScreen:
    def __init__(self):
        pass

# メインループ
def main():
    resources = Resource()
    state = GameState.start_screen
    screens = {
        GameState.start_screen: StartScrean(resources),
        GameState.character_select: CharacterSelect(resources),
        GameState.cource_select: CourceSelect(resources),
        GameState.time_attack: TimeAttack(resources),
        # GameState.result_screen: ResultScreen(resources),
        # GameState.credit_screen: CreditScreen(resources),
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