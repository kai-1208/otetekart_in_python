import pygame as pg
from src.config import WINDOW_SIZE, FPS, CAPTION, GameState
from src.resources import Resource
from src.states.start_screen import StartScreen
from src.states.character_select import CharacterSelect
from src.states.course_select import CourseSelect
from src.states.time_attack import TimeAttack
from src.states.vs_race import VSRace
from src.states.how_to_play import HowToPlayScreen
from src.states.credits import CreditScreen

def main():
    pg.init()
    screen = pg.display.set_mode(WINDOW_SIZE)
    clock = pg.time.Clock()
    pg.display.set_caption(CAPTION)

    resources = Resource()
    state = GameState.START_SCREEN
    
    screens = {
        GameState.START_SCREEN: StartScreen(resources),
        GameState.CHARACTER_SELECT: CharacterSelect(resources),
        GameState.COURSE_SELECT: CourseSelect(resources),
        GameState.TIME_ATTACK: TimeAttack(resources),
        GameState.VS_RACE: VSRace(resources),
        GameState.HOW_TO_PLAY: HowToPlayScreen(resources),
        GameState.CREDIT_SCREEN: CreditScreen(resources),
    }

    running = True
    while running:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False

        if state in screens:
            new_state = screens[state].run(screen, events)
            if new_state == "quit":
                running = False
            else:
                if new_state == GameState.TIME_ATTACK and state != GameState.TIME_ATTACK:
                    screens[GameState.TIME_ATTACK].reset()
                if new_state == GameState.VS_RACE and state != GameState.VS_RACE:
                    screens[GameState.VS_RACE].reset()
                state = new_state

        pg.display.update()
        clock.tick(FPS)
        pg.display.set_caption(f"{CAPTION} FPS: {int(clock.get_fps())}")

    pg.quit()

if __name__ == "__main__":
    main()