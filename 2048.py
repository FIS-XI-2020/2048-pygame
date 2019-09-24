"""
    2048 in Python implemented using pygame and django

    CBSE Computer Science project by:
        Adithya R (@ghostrider-reborn)
        Mohan S (@Autobahn1racer)
        Vansh U
        ~ class XII A, 2019-20, FIS
"""

import pygame, sys, random, itertools, time, os, django
from selenium import webdriver
from pygame.locals import *
from enum import Enum
from django.conf import settings
from website.website.settings import DATABASES

# configure django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'website.mainwebsite'
]
settings.configure(DATABASES=DATABASES, INSTALLED_APPS=INSTALLED_APPS)
django.setup()

from website.mainwebsite.models import leaderboard

# set some defaults
BOARD_WIDTH = 4
BOARD_HEIGHT = 4
BOARD_OUTER_LINE_WIDTH = 4
BLOCK_SIZE = 100
MARGIN_SIZE = 20
TITLE_SIZE = 52
BUTTON_FONT_SIZE = 35
SMALL_FONT_SIZE = 48
FONT_SIZE = 64
RESULT_SIZE = 32
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAX_SCORE = 2048
INIT_SCORE = 2
FPS = 30

# check window size
assert (BOARD_WIDTH * (BLOCK_SIZE + MARGIN_SIZE) < WINDOW_WIDTH) and \
       (BOARD_HEIGHT * (BLOCK_SIZE + MARGIN_SIZE) + TITLE_SIZE < WINDOW_HEIGHT), \
       'Window size is too small!'

X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * (BLOCK_SIZE + MARGIN_SIZE))) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * (BLOCK_SIZE + MARGIN_SIZE))) / 2 + TITLE_SIZE / 2)
TITLE_CENTER = (WINDOW_WIDTH // 2, Y_MARGIN // 2)

# set result types
class Result(Enum):
    Win = 1
    Lost = 0

# define some colours
class Color(Enum):
    White = (255, 255, 255)
    DeepOrange = (234, 120, 33)
    Black = (0, 0, 0)
    LightRed = (230, 0, 0)
    LightGreen = (0, 240, 0)
    LightBlue = (51, 153, 255)
    Gray = (128, 128, 128)
    Green = (0, 180, 0)
    Red = (190, 0, 0)
    Blue = (0, 102, 204)
    Fuschia = (255, 0, 255)
    Orange = (255, 69, 0)
    WinScr = (0, 220, 0)
    LoseScr = (255, 153, 51)
    Block2 = (204, 255, 255)
    Block4 = (153, 255, 255)
    Block8 = (102, 255, 255)
    Block16 = (0, 255, 255)
    Block32 = (0, 153, 153)
    Block64 = (51, 153, 255)
    Block128 = (0, 102, 204)
    Block256 = (0, 76, 153)
    Block512 = (127, 0, 255)
    Block1024 = (153, 51, 255)
    Block2048 = (153, 0, 153)
    TextLight = (255, 244, 234)
    TextDark = (30, 30, 30)

# initialize score as 0
current_score = 0

# set some default colours
TEXT_COLOR = Color.TextLight.value
WL_TEXT_COLOR = Color.TextDark.value
BOARD_TEXT_COLOR = Color.TextDark.value
COLOR_SWITCHER = {
    2: Color.Block2.value,
    4: Color.Block4.value,
    8: Color.Block8.value,
    16: Color.Block16.value,
    32: Color.Block32.value,
    64: Color.Block64.value,
    128: Color.Block128.value,
    256: Color.Block256.value,
    512: Color.Block512.value,
    1024: Color.Block1024.value,
    2048: Color.Block2048.value,
}

# set slide directions
class Direction(Enum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3

SLIDE_SWITCHER = {
    Direction.Up: [0, BOARD_HEIGHT, 1, 'coordinate_x', 'coordinate_y', BOARD_WIDTH],
    Direction.Down: [BOARD_HEIGHT - 1, -1, -1, 'coordinate_x', 'coordinate_y', BOARD_WIDTH],
    Direction.Left: [0, BOARD_WIDTH, 1, 'coordinate_y', 'coordinate_x', BOARD_HEIGHT],
    Direction.Right: [BOARD_WIDTH - 1, -1, -1, 'coordinate_y', 'coordinate_x', BOARD_HEIGHT],
}

# Movement of blocks, mergeing, generating new blocks etc
class Block:
    def __init__(self, x=random.randint(0, 3), y=random.randint(0, 3)):
        self.coordinate_x = x
        self.coordinate_y = y
        self.score = INIT_SCORE
        self.moved = False
        self.slide_enable = True
        self.next_coordinate_x = x
        self.next_coordinate_y = y

class Board:
    def __init__(self):
        self.blocks = [Block(), ]
        self.max_score = max([block.score for block in self.blocks])
        self.next_direction = Direction.Up

    def handle_block_slide(self, direction):
        ''' Moves the blocks in the specified direction '''
        self.next_direction = direction
        # check each row/column (depending on direction)
        for line_col_idx in range(SLIDE_SWITCHER[direction][5]):
            # blocks in same row/column, idx in current row/column
            current_blocks = [(block, getattr(block, SLIDE_SWITCHER[direction][4])) for block in self.blocks if
                              getattr(block, SLIDE_SWITCHER[direction][3]) == line_col_idx]
            # search: [idx_boundary -> idx_move_start) by idx_step
            current_blocks.sort(key=lambda row: row[1], reverse=False if (SLIDE_SWITCHER[direction][2] == 1) else True)
            previous_idx = -1
            for block in current_blocks:
                if block[1] == SLIDE_SWITCHER[direction][0]:  # element on boundary
                    setattr(block[0], 'slide_enable', False)
                    setattr(block[0], 'next_' + SLIDE_SWITCHER[direction][3], line_col_idx)
                    setattr(block[0], 'next_' + SLIDE_SWITCHER[direction][4], SLIDE_SWITCHER[direction][0])
                else:  # not boundary ehlement
                    if (block[1] - SLIDE_SWITCHER[direction][2] not in [row[1] for row in current_blocks]) or \
                            (getattr(current_blocks[previous_idx][0], 'slide_enable') is True):
                        setattr(block[0], 'slide_enable', True)
                        setattr(block[0], 'next_' + SLIDE_SWITCHER[direction][3], line_col_idx)
                        # calc next coordinate
                        if previous_idx == -1:
                            setattr(block[0], 'next_' + SLIDE_SWITCHER[direction][4], SLIDE_SWITCHER[direction][0])
                        else:
                            setattr(block[0], 'next_' + SLIDE_SWITCHER[direction][4],
                                    getattr(current_blocks[previous_idx][0],
                                            'next_' + SLIDE_SWITCHER[direction][4]) + SLIDE_SWITCHER[direction][2])
                previous_idx += 1

    def slide_block(self):
        ''' Moves the blocks in the specified direction by 1 unit '''
        for block in self.blocks:
            if block.slide_enable:
                block.coordinate_x = block.next_coordinate_x
                block.coordinate_y = block.next_coordinate_y
                block.moved = True
                block.slide_enable = False

    def merge_block(self, direction):
        ''' Merges the blocks of same value '''
        for line_col_idx in range(SLIDE_SWITCHER[direction][5]):
            current_blocks = [(block, getattr(block, SLIDE_SWITCHER[direction][4]))
                              for block in self.blocks if getattr(block, SLIDE_SWITCHER[direction][3]) == line_col_idx]
            if len(current_blocks) <= 1: continue
            else:
                # merge: (idx_move_start -> idx_boundary] by idx_step
                current_blocks.sort(key=lambda row: row[1], reverse=False if (SLIDE_SWITCHER[direction][2] == -1) else True)
                next_idx = 1
                for block in current_blocks:
                    if next_idx >= len(current_blocks): break
                    else:
                        if getattr(block[0], 'score') == getattr(current_blocks[next_idx][0], 'score'):
                            setattr(current_blocks[next_idx][0], 'score', 2 * getattr(block[0], 'score'))
                            self.blocks.remove(block[0])
                    next_idx += 1

    def generate_block(self):
        ''' Generates a random block and inserts it anywhere '''
        if len(self.blocks) >= (BOARD_WIDTH * BOARD_HEIGHT): return
        all_position = [(x, y) for x, y in itertools.product(range(BOARD_WIDTH), range(BOARD_HEIGHT))]
        for block in self.blocks:
            (x, y) = (block.coordinate_x, block.coordinate_y)
            all_position.remove((x, y))
        random.shuffle(all_position)
        position_insert = all_position.pop()
        self.blocks.append(Block(position_insert[0], position_insert[1]))

    def slide(self, direction):
        ''' All-in-one function to be used from main() '''
        self.handle_block_slide(direction)
        self.slide_block()
        self.merge_block(direction)
        self.generate_block()

    # default functions to be used from main()
    get_max_score = lambda self: max([block.score for block in self.blocks])
    get_block_num = lambda self: len(self.blocks)

def mainmenu():
    ''' Main Menu of the game '''
    global BG_OBJ, MUTE_OBJ, UNMUTE_OBJ, BACK_OBJ, muted, browser, current_score

    LOGO_OBJ = pygame.image.load("res/logo.png").convert_alpha()
    LOGO_RECT = LOGO_OBJ.get_rect(centerx = (WINDOW_WIDTH // 2), top = 75)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
        WINDOW.blit(BG_OBJ, (0, 0))
        WINDOW.blit(LOGO_OBJ, LOGO_RECT)

        # Mute/unmute button
        if not muted: WINDOW.blit(MUTE_OBJ, (720, 15))
        else: WINDOW.blit(UNMUTE_OBJ, (720, 15))
        if mouse_status(725, 20, 50, 50)[1]:
            if not muted: pygame.mixer.music.pause()
            else: pygame.mixer.music.unpause()
            muted = not muted

        # the play button - when clicked, opens the login page and redirects
        # back to the game window when the user has logged in or registered
        if draw_button('Play', "Green", BUTTON_FONT_SIZE, 200):
            openLoginPage()
            return
        # the quit button - when clicked, updates score in the leaderboard if
        # the user played the game, and then quits
        elif draw_button('Quit', "Red", BUTTON_FONT_SIZE, 410):
            if current_score > 0: updateLeaderboard(current_score)
            quit()
        # leaderboard button - launches the leaderboard page
        elif draw_button('Leaderboard', "Blue", BUTTON_FONT_SIZE, 305):
            browser = openbrowser()
            browser.get('http://localhost:8000/leaderboard')

        pygame.display.update()
        FPS_CLOCK.tick(FPS)

def game():
    ''' The main game '''
    global FPS_CLOCK, WINDOW, FONT_OBJ, TITLE_OBJ, BLOCK_BOARD, BG_OBJ, MUTE_OBJ, UNMUTE_OBJ, BACK_OBJ, muted, current_score

    # initialize the pygame window
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BLOCK_BOARD = pygame.Rect(X_MARGIN - BOARD_OUTER_LINE_WIDTH, Y_MARGIN - BOARD_OUTER_LINE_WIDTH,
                              (BLOCK_SIZE + MARGIN_SIZE) * BOARD_WIDTH + BOARD_OUTER_LINE_WIDTH * 2 - MARGIN_SIZE,
                              (BLOCK_SIZE + MARGIN_SIZE) * BOARD_HEIGHT + BOARD_OUTER_LINE_WIDTH * 2 - MARGIN_SIZE)
    # set font
    FONT_OBJ = pygame.font.Font('res/fonts/Slate.ttf', FONT_SIZE)
    TITLE_OBJ = pygame.font.Font('res/fonts/PixelOperator-Bold.ttf', TITLE_SIZE)

    # initialize the 2048 board
    main_board = Board()
    title_text = 'Your Score: '
    muted = False

    # load em images
    BG_OBJ = pygame.image.load("res/background.jpg")
    MUTE_OBJ = pygame.image.load("res/unmute.png").convert_alpha()
    UNMUTE_OBJ = pygame.image.load("res/mute.png").convert_alpha()
    BACK_OBJ = pygame.image.load("res/backbutton.png").convert_alpha()

    # play some tunes and start with the main menu
    pygame.display.set_caption('2048 Game for MeAndTheBois™')
    pygame.mixer.music.load('res/music.mp3')
    pygame.mixer.music.play(-1)
    mainmenu()

    # Main game loop
    while True:
        """
        DEBUG
        handle_win_or_lost(Result.Win)
        handle_win_or_lost(Result.Lost)
        """
        WINDOW.blit(BG_OBJ, (0, 0))
        WINDOW.blit(BACK_OBJ, (20, 20))
        pygame.draw.rect(WINDOW, Color.DeepOrange.value, BLOCK_BOARD, BOARD_OUTER_LINE_WIDTH)

        for event in pygame.event.get():
            # when the user clicks the exit button, save the score in the
            # leaderboard and then exit
            if event.type == QUIT:
                updateLeaderboard(current_score)
                quit()
            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a): main_board.slide(Direction.Left)
                elif event.key in (K_RIGHT, K_d): main_board.slide(Direction.Right)
                elif event.key in (K_UP, K_w): main_board.slide(Direction.Up)
                elif event.key in (K_DOWN, K_s): main_board.slide(Direction.Down)
                elif event.key == K_ESCAPE: mainmenu()

        # Mute/unmute button
        if not muted: WINDOW.blit(MUTE_OBJ, (720, 15))
        else: WINDOW.blit(UNMUTE_OBJ, (720, 15))
        if mouse_status(725, 20, 50, 50)[1]:
            if not muted: pygame.mixer.music.pause()
            else: pygame.mixer.music.unpause()
            muted = not muted

        # Back button (go to main menu)
        if mouse_status(20, 20, 50, 50)[1]: mainmenu()

        current_score = main_board.get_max_score()
        draw_blocks(main_board)

        if len(main_board.blocks) >= (BOARD_WIDTH * BOARD_HEIGHT):
            pygame.time.wait(1000)
            handle_win_or_lost(Result.Lost)
            main_board = Board()
        elif current_score < 2048:
            title = title_text + str(current_score)
            draw_title(title)
        else:
            pygame.time.wait(1000)
            handle_win_or_lost(Result.Win)
            main_board = Board()

        pygame.display.update()
        FPS_CLOCK.tick(FPS)

def quit():
    ''' Neatly logout and quit the game '''
    pygame.quit()
    if os.path.isfile("website/authinfo.txt"):
        os.remove("website/authinfo.txt")
        browser = openbrowser()
        browser.get('http://localhost:8000/logout')
        time.sleep(2)
        browser.close()
    sys.exit()

def openbrowser():
    ''' Opens a selenium webdriver browser window '''
    if os.name == 'nt':
        try: browser = webdriver.Firefox(executable_path = 'res/geckodriver.exe')
        except: browser = webdriver.Chrome('res/chromedriver.exe')
    else:
        try: browser = webdriver.Firefox(executable_path = 'res/geckodriver')
        except: browser = webdriver.Chrome('res/chromedriver')
    return browser

def openLoginPage():
    ''' Opens the register/login page and waits until the user has logged in
        and exports the username once logged in '''
    global username

    # logic: the django view function writes to a file authinfo.txt
    # once the user has succesfully logged in. until the file has been
    # written, keep waiting, try every 2 sec and when the user has logged
    # in, get the username from the text file and export it
    # this file is deleted when the user exits the game
    # TODO: use a more secure method for checking login
    if not os.path.isfile("website/authinfo.txt"):
        browser = openbrowser()
        browser.get('http://localhost:8000/login')
        while not os.path.isfile("website/authinfo.txt"):
            print("User has not logged in yet! Waiting for 2 secs...")
            time.sleep(2)
        time.sleep(1)
        browser.close()

    with open("website/authinfo.txt", "r") as authinfo:
        username = ((authinfo.readlines())[0].split())[0]
        print("\nLogged in as user:", username)

def updateLeaderboard(score):
    ''' Handles updating or adding score in leaderboard, using django models '''
    global username

    # get the level based on the score
    if score <= 64: level = "Beginner"
    elif score <= 64: level = "Amateur"
    elif score <= 128: level = "Learner"
    elif score <= 256: level = "Semi-pro"
    elif score <= 1024: level = "Pro"
    else: level = "Champion"

    # check and update entry of user if already exists, otherwise create new
    if leaderboard.objects.filter(username=username).exists():
        user_record = leaderboard.objects.get(username=username)
        user_record.total_played += 1
        if user_record.total_played > 8 and score == 2048:
            user_record.player_level = "Veteran"
        # update the score only if score is higher than the existing top score
        if score > user_record.top_score:
            user_record.top_score = score
            user_record.player_level = level
    else:
        user_record = leaderboard(username=username, total_played=1, top_score=score, player_level=level)

    user_record.save()

def draw_blocks(board_in):
    ''' Render all blocks on the screen '''
    for block in board_in.blocks:
        if block.score > 64:
            BOARD_TEXT_COLOR = Color.TextLight.value
            FONT_OBJ = pygame.font.Font('res/fonts/Slate.ttf', SMALL_FONT_SIZE)
        else:
            BOARD_TEXT_COLOR = Color.TextDark.value
            FONT_OBJ = pygame.font.Font('res/fonts/Slate.ttf', FONT_SIZE)

        left = X_MARGIN + (BLOCK_SIZE + MARGIN_SIZE) * block.coordinate_x
        top = Y_MARGIN + (BLOCK_SIZE + MARGIN_SIZE) * block.coordinate_y
        block_rect_obj = pygame.Rect(left, top, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(WINDOW, COLOR_SWITCHER[block.score], block_rect_obj)
        text_surface_obj = FONT_OBJ.render(str(block.score), True, BOARD_TEXT_COLOR)
        text_rect_obj = text_surface_obj.get_rect(center = block_rect_obj.center)
        WINDOW.blit(text_surface_obj, text_rect_obj)

def draw_title(title, y = False, color = TEXT_COLOR):
    ''' Render a title text according to TITLE_OBJ '''
    text_surface_obj = TITLE_OBJ.render(title, True, color)
    if y: text_rect_obj = text_surface_obj.get_rect(top = y, centerx = WINDOW_WIDTH // 2)
    else: text_rect_obj = text_surface_obj.get_rect(center = TITLE_CENTER)
    WINDOW.blit(text_surface_obj, text_rect_obj)

def handle_win_or_lost(result):
    ''' Win/lose screen '''
    global current_score

    if result == Result.Win:
        BACKGROUND_COLOR = Color.WinScr.value
        smiley_img = pygame.image.load("res/happy_smiley.png")
        title = 'You Win. Congratulations!\n\nHit "Esc" key to go back to main menu,\nor any other key to restart.'
    else:
        BACKGROUND_COLOR = Color.LoseScr.value
        smiley_img = pygame.image.load("res/sad_smiley.png")
        title = 'You Lose. Better luck next time!\n\nHit "Esc" key to go back to main menu,\nor any other key to restart.'

    text_y = Y_MARGIN + int(TITLE_SIZE / 2) + 130
    result_font = pygame.font.Font('res/fonts/Slate.ttf', RESULT_SIZE)
    smiley_obj = smiley_img.get_rect(top = Y_MARGIN - 55, centerx =  WINDOW_WIDTH // 2)

    WINDOW.fill(BACKGROUND_COLOR)
    WINDOW.blit(smiley_img, smiley_obj)

    lines = title.split('\n')
    draw_title(lines[0], text_y, WL_TEXT_COLOR)
    text_y += 30

    for text in lines[1:]:
        text_y += int(RESULT_SIZE * 1.2)
        text_surface_obj = result_font.render(text, True, WL_TEXT_COLOR, BACKGROUND_COLOR)
        text_rect_obj = text_surface_obj.get_rect(top = text_y, centerx = WINDOW_WIDTH // 2)
        WINDOW.blit(text_surface_obj, text_rect_obj)

    pygame.display.update()
    pygame.time.wait(1000)
    pygame.event.clear()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                updateLeaderboard(current_score)
                mainmenu()
                return
            elif event.type == KEYUP: quit()
        pygame.display.update()
        FPS_CLOCK.tick(FPS)

def draw_button(text, colorname, fontsize, button_y):
    ''' Function to create a center aligned button with text in it and highlight
        it when mouse is hovered on it. Also returns True when clicked on it. '''
    color = eval('Color.%s.value' % colorname)
    font = pygame.font.Font("res/fonts/PixelOperator8-Bold.ttf", fontsize)
    text_ =  font.render(text, False, Color.Black.value)

    text_w = text_.get_width()
    text_h = text_.get_height()

    button_x = (WINDOW_WIDTH // 2) - (text_w // 2) - 20
    button_w = text_w + 40
    button_h = text_h + 20

    text_rect = text_.get_rect(top = button_y+10, centerx = (WINDOW_WIDTH // 2))
    pygame.draw.rect(WINDOW, color, [button_x, button_y, button_w, button_h])

    # Change draw_button colour to light on mouseover
    if mouse_status(button_x, button_y, button_w, button_h)[0]:
        color = eval('Color.%s.value' % ("Light"+colorname))
        pygame.draw.rect(WINDOW, color, [button_x, button_y, button_w, button_h])
    if mouse_status(button_x, button_y, button_w, button_h)[1]: return True

    WINDOW.blit(text_, text_rect)

def mouse_status(x, y, w, h):
    ''' Returns mouse status on a given rect as (<mouse-hover>, <mouse-click>) bools '''
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    for i, j in itertools.product(range(x, x+w), range(y, y+h)):
        if i == mouse[0] and j == mouse[1]:
            if not click[0]: return True, False
            else:
                pygame.time.wait(100)
                return True, True

    return False, False

if __name__ == "__main__":
    try: game()
    except KeyboardInterrupt: pass
    updateLeaderboard(current_score)
    quit()
