import pygame as pg
import os
from src.config import FONT_PATH, IMG_DIR
from src.models import CharacterParameter
from src.network import NetworkManager

class Resource:
    def __init__(self):
        # Networking (Persistent)
        self.network = NetworkManager()
        
        # Load background images
        self.start_screen_bg = pg.transform.scale(
            pg.image.load(os.path.join(IMG_DIR, "start_screen_bg.png")),
            (pg.image.load(os.path.join(IMG_DIR, "start_screen_bg.png")).get_width() * 5, 
             pg.image.load(os.path.join(IMG_DIR, "start_screen_bg.png")).get_height() * 5)
        )
        self.character_select_bg = pg.transform.scale(
            pg.image.load(os.path.join(IMG_DIR, "character_select_bg.png")),
            (pg.image.load(os.path.join(IMG_DIR, "character_select_bg.png")).get_width() * 5,
             pg.image.load(os.path.join(IMG_DIR, "character_select_bg.png")).get_height() * 5)
        )

        self.font = pg.font.Font(FONT_PATH, 20)

        arrow_scale = 2
        right_arrow_img = pg.image.load(os.path.join(IMG_DIR, "right_arrow.png"))
        self.right_arrow = pg.transform.scale(
            right_arrow_img, 
            (right_arrow_img.get_width() * arrow_scale, right_arrow_img.get_height() * arrow_scale)
        )
        self.left_arrow = pg.transform.flip(self.right_arrow, True, False)

        self.otete_images = {}
        otete_scale = 4
        for i in range(4):
            otete = pg.image.load(os.path.join(IMG_DIR, f"otetekart{i+1}.png"))
            self.otete_images[i] = {
                "select": pg.transform.scale(otete.subsurface(pg.Rect(0, 0, 50, 50)),
                                             (otete.subsurface(pg.Rect(0, 0, 50, 50)).get_width() * otete_scale,
                                              otete.subsurface(pg.Rect(0, 0, 50, 50)).get_height() * otete_scale)),
                "left": pg.transform.scale(otete.subsurface(pg.Rect(50, 0, 50, 50)),
                                           (otete.subsurface(pg.Rect(50, 0, 50, 50)).get_width() * otete_scale,
                                            otete.subsurface(pg.Rect(50, 0, 50, 50)).get_height() * otete_scale)),
                "center": pg.transform.scale(otete.subsurface(pg.Rect(100, 0, 50, 50)),
                                             (otete.subsurface(pg.Rect(100, 0, 50, 50)).get_width() * otete_scale,
                                              otete.subsurface(pg.Rect(100, 0, 50, 50)).get_height() * otete_scale)),
                "right": pg.transform.scale(otete.subsurface(pg.Rect(150, 0, 50, 50)),
                                            (otete.subsurface(pg.Rect(150, 0, 50, 50)).get_width() * otete_scale,
                                             otete.subsurface(pg.Rect(150, 0, 50, 50)).get_height() * otete_scale)),
            }
        
        self.course_images = {} # Renamed from cource_images
        for i in range(4):
            # Keep filename as cource{i+1}.png as per disk
            course = pg.image.load(os.path.join(IMG_DIR, f"cource{i+1}.png")) 
            self.course_images[i] = {
                "collision": course.subsurface(pg.Rect(0, 0, 200, 200)),
                "show": course.subsurface(pg.Rect(200, 0, 200, 200)),
                "sky": course.subsurface(pg.Rect(400, 0, 200, 50)),
            }
        
        self.player = pg.image.load(os.path.join(IMG_DIR, "player.png"))
        
        self.current_otete = 0
        self.current_course = 0 # Renamed from current_cource
        self.game_mode = "TIME_ATTACK"

        self.character_parameter = [
            CharacterParameter("otete1", 2, 5, 4),
            CharacterParameter("otete2", 3, 4, 4),
            CharacterParameter("otete3", 4, 3, 2),
            CharacterParameter("otete4", 5, 2, 1),
        ]
