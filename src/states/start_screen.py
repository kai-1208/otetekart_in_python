import pygame as pg
from src.config import GameState, BUTTON_COLOR, BUTTON_HOVER_COLOR
from src.ui import Button

class StartScreen:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(400, 250, 400, 80, "Time Attack", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.button_vs = Button(400, 350, 400, 80, "VS Race", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.button2 = Button(400, 450, 400, 80, "How to Play", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.button3 = Button(400, 550, 400, 80, "Credit", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)

    def run(self, screen, events):
        screen.blit(self.resources.start_screen_bg, (0, 0))
        self.button1.draw(screen)
        self.button_vs.draw(screen)
        self.button2.draw(screen)
        self.button3.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if self.button1.is_clicked(event):
                self.resources.game_mode = "TIME_ATTACK"
                return GameState.CHARACTER_SELECT
            if self.button_vs.is_clicked(event):
                self.resources.game_mode = "VS_RACE"
                return GameState.CHARACTER_SELECT
            if self.button2.is_clicked(event):
                return GameState.HOW_TO_PLAY
            if self.button3.is_clicked(event):
                return GameState.CREDIT_SCREEN
        return GameState.START_SCREEN
