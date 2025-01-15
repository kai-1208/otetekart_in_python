import pygame as pg

pg.init() # 初期化
window_size = (800, 600)
screen = pg.display.set_mode(window_size)
clock = pg.time.Clock()
pg.display.set_caption("otete kart")

raw1 = pg.image.load("./img/otetekart2.png") # 画像の読み込み
pose_p = pg.Vector2(0, 0) # ポーズの位置
pose_s = pg.Vector2(50, 50) # ポーズのサイズ
tmp = raw1.subsurface(pg.Rect(pose_p, pose_s)) # ポーズの切り出し

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill((0, 0, 0)) # 画面を黒にする

    screen.blit(tmp, (100, 100)) # 画像を描画

    pg.display.flip() # 画面を更新

pg.quit() # Pygameの終了