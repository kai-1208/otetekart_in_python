import pygame as pg

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

        self.time_attack_button = Button(500, 300, 200, 100, "Time Attack", font, (26, 175, 0), (255, 255, 255))
        self.credit_button = Button(500, 400, 200, 100, "Credit", font, (26, 175, 0), (255, 255, 255))

        self.right_arrow = pg.image.load("./img/right_arrow.png")
        self.left_arrow = pg.transform.flip(self.right_arrow, True, False)

        self.otete1 = pg.image.load("./img/otetekart1.png")
        self.otete1_select = self.otete1.subsurface(pg.Rect(0, 0, 50, 50))
        self.otete1_right = self.otete1.subsurface(pg.Rect(50, 0, 50, 50))
        self.otete1_center = self.otete1.subsurface(pg.Rect(100, 0, 50, 50))
        self.otete1_left = self.otete1.subsurface(pg.Rect(150, 0, 50, 50))
        self.otete2 = pg.image.load("./img/otetekart2.png")
        self.otete2_select = self.otete2.subsurface(pg.Rect(0, 0, 50, 50))
        self.otete2_right = self.otete2.subsurface(pg.Rect(50, 0, 50, 50))
        self.otete2_center = self.otete2.subsurface(pg.Rect(100, 0, 50, 50))
        self.otete2_left = self.otete2.subsurface(pg.Rect(150, 0, 50, 50))
        self.otete3 = pg.image.load("./img/otetekart3.png")
        self.otete3_select = self.otete3.subsurface(pg.Rect(0, 0, 50, 50))
        self.otete3_right = self.otete3.subsurface(pg.Rect(50, 0, 50, 50))
        self.otete3_center = self.otete3.subsurface(pg.Rect(100, 0, 50, 50))
        self.otete3_left = self.otete3.subsurface(pg.Rect(150, 0, 50, 50))
        self.otete4 = pg.image.load("./img/otetekart4.png")
        self.otete4_select = self.otete4.subsurface(pg.Rect(0, 0, 50, 50))
        self.otete4_right = self.otete4.subsurface(pg.Rect(50, 0, 50, 50))
        self.otete4_center = self.otete4.subsurface(pg.Rect(100, 0, 50, 50))
        self.otete4_left = self.otete4.subsurface(pg.Rect(150, 0, 50, 50))


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

        self.resources.time_attack_button.draw(screen)
        self.resources.credit_button.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if self.resources.time_attack_button.is_clicked(event):
                return GameState.character_select
            if self.resources.credit_button.is_clicked(event):
                return GameState.credit_screen
        return GameState.start_screen


# キャラクター選択画面
class CharacterSelect:
    def __init__(self, resources):
        self.resources = resources

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))


# コース選択画面
class CourceSelect:
    def __init__(self):
        pass

# タイムアタック画面
class TimeAttack:
    def __init__(self):
        pass

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
        # GameState.cource_select: CourceSelect(resources),
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
        # if state == GameState.start_screen:
        #     screens[GameState.start_screen].run(screen)
        # elif state == GameState.character_select:
        #     screens[GameState.character_select].run(screen)
        # elif state == GameState.cource_select:
        #     screens[GameState.cource_select].run(screen)
        # elif state == GameState.time_attack:
        #     screens[GameState.time_attack].run(screen)
        # elif state == GameState.result_screen:
        #     screens[GameState.result_screen].run(screen)
        # elif state == GameState.credit_screen:
        #     screens[GameState.credit_screen].run(screen)

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