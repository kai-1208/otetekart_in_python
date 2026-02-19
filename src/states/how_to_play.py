import pygame as pg
from src.config import GameState, BUTTON_COLOR, BUTTON_HOVER_COLOR
from src.ui import Button

class HowToPlayScreen:
    def __init__(self, resources):
        self.resources = resources
        self.font = self.resources.font
        self.button = Button(400, 500, 400, 100, "Back to Start Screen", self.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)

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
                return GameState.START_SCREEN
        return GameState.HOW_TO_PLAY
