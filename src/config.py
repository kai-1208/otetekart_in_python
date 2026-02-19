
class GameState:
    START_SCREEN = "startScreen"
    CHARACTER_SELECT = "characterSelect"
    COURSE_SELECT = "courceSelect" # Kept the string value for compatibility if needed, but corrected key
    TIME_ATTACK = "timeAttack"
    VS_RACE = "vsRace"
    HOW_TO_PLAY = "howToPlay"
    CREDIT_SCREEN = "creditScreen"

# Window Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
FPS = 60
CAPTION = "otete kart"

# Colors
WHITE = (255, 255, 255)
BUTTON_COLOR = (26, 175, 0)
BUTTON_HOVER_COLOR = (76, 225, 50)

# Paths
FONT_PATH = "./fonts/cellar.ttf"
IMG_DIR = "./img"
