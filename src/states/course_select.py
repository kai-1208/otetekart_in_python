import pygame as pg
from src.config import GameState, BUTTON_COLOR, BUTTON_HOVER_COLOR
from src.ui import Button
import time

class CourseSelect:
    def __init__(self, resources):
        self.resources = resources
        self.button1 = Button(0, 500, 400, 100, "Back to Character Select", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.button2 = Button(400, 500, 400, 100, "Go to Race", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        self.network = None
        self.last_fetch_time = 0
        self.button2 = Button(400, 500, 400, 100, "Go to Time Attack", self.resources.font, BUTTON_COLOR, BUTTON_HOVER_COLOR)

    def run(self, screen, events):
        screen.blit(self.resources.character_select_bg, (0, 0))
        # Note: Using course_images instead of cource_images
        screen.blit(self.resources.course_images[self.resources.current_course]["show"], (300, 200))
        screen.blit(self.resources.left_arrow, (200, 300))
        screen.blit(self.resources.right_arrow, (500, 300))
        
        # VS Mode Logic
        if self.resources.game_mode == "VS_RACE":
            # Rate limit fetch
            if time.time() - self.last_fetch_time > 1.0:
                self.resources.network.get_room_counts()
                self.last_fetch_time = time.time()
                
            # Display Counts
            count = self.resources.network.room_counts.get(str(self.resources.current_course), 0)
            # JSON keys might be strings, server sends {0: n}. requests json converts keys to str? 
            # Usually json keys are strings. 
            
            text = self.resources.font.render(f"Waiting Players: {count}", True, (255, 255, 255))
            screen.blit(text, (350, 150))
            
            self.button2.text = "Go to VS Race"
        else:
             self.button2.text = "Go to Time Attack"

        self.button1.draw(screen)
        self.button2.draw(screen)

        for event in events:
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if pg.Rect(200, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_course = (self.resources.current_course - 1) % 4
                if pg.Rect(500, 300, 100, 100).collidepoint(event.pos):
                    self.resources.current_course = (self.resources.current_course + 1) % 4
            if self.button1.is_clicked(event):
                return GameState.CHARACTER_SELECT
            if self.button2.is_clicked(event):
                if self.resources.game_mode == "VS_RACE":
                    return GameState.VS_RACE
                else:
                    return GameState.TIME_ATTACK
                return GameState.TIME_ATTACK
        return GameState.COURSE_SELECT
