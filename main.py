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

# リソース管理
class Resource:
    def __init__(self):
        self.start_screen_bg = pg.image.load("./img/start_screen_bg.png")
        self.start_screen_bg = pg.transform.scale(self.start_screen_bg, (self.start_screen_bg.get_width() * 5, self.start_screen_bg.get_height() * 5))


# スタート画面
class StartScrean:
    def __init__(self, resources):
        self.resources = resources

    def run(self, screen):
        screen.blit(self.resources.start_screen_bg, (0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                return GameState.character_select
        return GameState.start_screen


# キャラクター選択画面
class CharacterSelect:
    def __init__(self, resources):
        self.resources = resources

    # def run(self, screen):


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

# メインループ
def main():
    resources = Resource()
    state = GameState.start_screen
    screens = {
        GameState.start_screen: StartScrean(resources),
        # GameState.character_select: CharacterSelect(resources),
        # GameState.cource_select: CourceSelect(resources),
        # GameState.time_attack: TimeAttack(resources),
        # GameState.result_screen: None,
    }
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # ゲームの状態に応じて画面を描画
        if state == GameState.start_screen:
            screens[GameState.start_screen].run(screen)

        pg.display.update() # 画面を更新
        clock.tick(60) # 60FPSに設定

    pg.quit()

if __name__ == "__main__":
    main()