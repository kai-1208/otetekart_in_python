import pygame as pg
from src.config import GameState, BUTTON_COLOR, BUTTON_HOVER_COLOR
from src.ui import Button

class CreditScreen:
    def __init__(self, resources):
        self.resources = resources
        self.font = self.resources.font
        self.button = Button(400, 500, 400, 100, "Back to Start Screen", self.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)

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
                return GameState.START_SCREEN
        return GameState.CREDIT_SCREEN
