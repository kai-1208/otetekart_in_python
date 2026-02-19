import pygame as pg
from src.config import GameState, BUTTON_COLOR, BUTTON_HOVER_COLOR
from src.ui import Button

class CharacterSelect:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(0, 500, 400, 100, "Back to Start Screen", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.button2 = Button(400, 500, 400, 100, "Go to Course Select", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))
        screen.blit(self.resources.otete_images[self.resources.current_otete]["select"], (300, 200))
        screen.blit(self.resources.left_arrow, (200, 300))
        screen.blit(self.resources.right_arrow, (500, 300))
        self.button1.draw(screen)
        self.button2.draw(screen)

        character_name = self.resources.character_parameter[self.resources.current_otete].name
        speed = self.resources.character_parameter[self.resources.current_otete].speed
        acceleration = self.resources.character_parameter[self.resources.current_otete].acceleration
        handling = self.resources.character_parameter[self.resources.current_otete].handling
        
        character_name_text = self.resources.font.render(f"Name : {character_name}", True, (255, 255, 255))
        parameter_text = self.resources.font.render(f"Speed : {speed}, Acceleration : {acceleration}, Handling : {handling}", True, (255, 255, 255))
        screen.blit(character_name_text, (50, 50))
        screen.blit(parameter_text, (50, 100))

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Left Arrow Click
                if pg.Rect(200, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_otete = (self.resources.current_otete - 1) % 4
                # Right Arrow Click
                if pg.Rect(500, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_otete = (self.resources.current_otete + 1) % 4
            
            if self.button1.is_clicked(event):
                return GameState.START_SCREEN
            if self.button2.is_clicked(event):
                return GameState.COURSE_SELECT
        return GameState.CHARACTER_SELECT
