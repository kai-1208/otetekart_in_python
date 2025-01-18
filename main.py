import pygame as pg
import numpy as np
import time

pg.init() # 初期化
window_size = (800, 600)
screen = pg.display.set_mode(window_size)
clock = pg.time.Clock()
pg.display.set_caption("otete kart")

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

        # self.otete1 = pg.image.load("./img/otetekart1.png")
        # self.otete1_select = self.otete1.subsurface(pg.Rect(0, 0, 50, 50))
        # self.otete1_left = self.otete1.subsurface(pg.Rect(50, 0, 50, 50))
        # self.otete1_center = self.otete1.subsurface(pg.Rect(100, 0, 50, 50))
        # self.otete1_right = self.otete1.subsurface(pg.Rect(150, 0, 50, 50))
        # self.otete2 = pg.image.load("./img/otetekart2.png")
        # self.otete2_select = self.otete2.subsurface(pg.Rect(0, 0, 50, 50))
        # self.otete2_left = self.otete2.subsurface(pg.Rect(50, 0, 50, 50))
        # self.otete2_center = self.otete2.subsurface(pg.Rect(100, 0, 50, 50))
        # self.otete2_right = self.otete2.subsurface(pg.Rect(150, 0, 50, 50))
        # self.otete3 = pg.image.load("./img/otetekart3.png")
        # self.otete3_select = self.otete3.subsurface(pg.Rect(0, 0, 50, 50))
        # self.otete3_left = self.otete3.subsurface(pg.Rect(50, 0, 50, 50))
        # self.otete3_center = self.otete3.subsurface(pg.Rect(100, 0, 50, 50))
        # self.otete3_right = self.otete3.subsurface(pg.Rect(150, 0, 50, 50))
        # self.otete4 = pg.image.load("./img/otetekart4.png")
        # self.otete4_select = self.otete4.subsurface(pg.Rect(0, 0, 50, 50))
        # self.otete4_left = self.otete4.subsurface(pg.Rect(50, 0, 50, 50))
        # self.otete4_center = self.otete4.subsurface(pg.Rect(100, 0, 50, 50))
        # self.otete4_right = self.otete4.subsurface(pg.Rect(150, 0, 50, 50))
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
                "show": cource.subsurface(pg.Rect(0, 0, 200, 200)),
                "collision": cource.subsurface(pg.Rect(200, 200, 200, 200)),
            }

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

        screen.blit(self.resources.cource_images[self.current_cource], (300, 200))

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
        # GameState.time_attack: TimeAttack(resources),
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

    pg.quit()

if __name__ == "__main__":
    main()