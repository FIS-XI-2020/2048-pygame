"""
    2048 in Python using pygame module
    [CBSE CS project 2019-20]
"""

import pygame, sys, random, itertools
from pygame.locals import *
from enum import Enum

BOARD_WIDTH = 4
BOARD_HEIGHT = 4
BOARD_OUTER_LINE_WIDTH = 4
BLOCK_SIZE = 100
MARGIN_SIZE = 20
TITLE_SIZE = 60
FONT_SIZE = 64
RESULT_SIZE = 35
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAX_SCORE = 2048
INIT_SCORE = 2
FPS = 30

# Check window size
assert (BOARD_WIDTH * (BLOCK_SIZE + MARGIN_SIZE) < WINDOW_WIDTH) and \
       (BOARD_HEIGHT * (BLOCK_SIZE + MARGIN_SIZE) + TITLE_SIZE < WINDOW_HEIGHT), \
       'Window size is too small!'
X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * (BLOCK_SIZE + MARGIN_SIZE))) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_HEIGHT * (BLOCK_SIZE + MARGIN_SIZE))) / 2 + TITLE_SIZE / 2)
TITLE_CENTER = (int(WINDOW_WIDTH / 2), int(Y_MARGIN / 2))

# Set Result
class Result(Enum):
    Win = 1
    Lost = 0

# Set Color
class Color(Enum):
    White = (255, 255, 255)
    DeepOrange = (234, 120, 33)
    white = (255, 255, 255)
    Black = (0,0,0)
    LightRed = (230, 0, 0)
    LightGreen = (0, 240, 0)
    LightBlue = (51, 153, 255)
    Gray = (128, 128, 128)
    Green = (0, 180, 0)
    Red = (190, 0, 0)
    Blue = (0, 102, 204)
    Fuschia = (255,0,255)
    Orange = (255,69,0)
    Block0 = (204, 192, 179)
    Block2 = (238, 228, 218)
    Block4 = (237, 224, 200)
    Block8 = (242, 177, 121)
    Block16 = (244, 149, 99)
    Block32 = (245, 121, 77)
    Block64 = (245, 93, 55)
    Block128 = (238, 232, 99)
    Block256 = (237, 176, 77)
    Block512 = (236, 176, 77)
    Block1024 = (235, 148, 55)
    Block2048 = (234, 120, 33)
    TextLight = (255, 244, 234)
    TextDark = (119, 110, 101)

BACKGROUND_COLOR = Color.Block0.value
TEXT_COLOR = Color.TextLight.value
BOARD_TEXT_COLOR = Color.TextDark.value
COLOR_SWITCHER = {
    0: Color.Block0.value,
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

# Set Direction
class Direction(Enum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3

# idx_boundary, idx_slide_start, idx_step, attr_name (col/line), attr_name (elem), range of another attr
SLIDE_SWITCHER = {
    Direction.Up: [0, BOARD_HEIGHT, 1, 'coordinate_x', 'coordinate_y', BOARD_WIDTH],
    Direction.Down: [BOARD_HEIGHT - 1, -1, -1, 'coordinate_x', 'coordinate_y', BOARD_WIDTH],
    Direction.Left: [0, BOARD_WIDTH, 1, 'coordinate_y', 'coordinate_x', BOARD_HEIGHT],
    Direction.Right: [BOARD_WIDTH - 1, -1, -1, 'coordinate_y', 'coordinate_x', BOARD_HEIGHT],
}

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
                else:  # not boundary element
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
        for block in self.blocks:
            if block.slide_enable:
                block.coordinate_x = block.next_coordinate_x
                block.coordinate_y = block.next_coordinate_y
                block.moved = True
                block.slide_enable = False

    def merge_block(self, direction):
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
        if len(self.blocks) >= (BOARD_WIDTH * BOARD_HEIGHT): return
        all_position = [(x, y) for x, y in itertools.product(range(BOARD_WIDTH), range(BOARD_HEIGHT))]
        for block in self.blocks:
            (x, y) = (block.coordinate_x, block.coordinate_y)
            assert ((x, y) in all_position), 'contain block(s) with invalid location ' + str((x, y))
            all_position.remove((x, y))
        random.shuffle(all_position)
        position_insert = all_position.pop()
        self.blocks.append(Block(position_insert[0], position_insert[1]))

    def slide(self, direction):
        self.handle_block_slide(direction)
        self.slide_block()
        self.merge_block(direction)
        self.generate_block()

    get_max_score = lambda self: max([block.score for block in self.blocks])
    get_block_num = lambda self: len(self.blocks)

def mainmenu():
    ''' Main Menu of the game '''
    BG_OBJ = pygame.image.load("res/background.jpg")
    LOGO_OBJ = pygame.image.load("res/logo.png").convert_alpha()
    MUTE_OBJ = pygame.image.load("res/unmute.png").convert_alpha()
    UNMUTE_OBJ = pygame.image.load("res/mute.png").convert_alpha()

    muted = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        WINDOW.blit(BG_OBJ, (0, 0))
        WINDOW.blit(LOGO_OBJ, (215, 75))

        if not muted: WINDOW.blit(MUTE_OBJ, (720, 15))
        else: WINDOW.blit(UNMUTE_OBJ, (720, 15))

        if is_clicked(725, 20, 50, 50):
            pygame.time.wait(100)
            if not muted: pygame.mixer.music.pause()
            else: pygame.mixer.music.unpause()
            muted = not muted

        play = draw_button('Play', "Green", 335, 200, 165, 60, 415, 230)
        highscore = draw_button('High Scores', "Blue", 245, 305, 355, 60, 425, 335)
        quit = draw_button('Quit', "Red", 335, 410, 165, 60, 415, 440)

        if quit: break
        elif play: return

        pygame.display.update()
        FPS_CLOCK.tick(FPS)

    pygame.quit()
    sys.exit()

def game():
    global FPS_CLOCK, WINDOW, FONT_OBJ, TITLE_OBJ, BLOCK_BOARD

    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BLOCK_BOARD = pygame.Rect(X_MARGIN - BOARD_OUTER_LINE_WIDTH, Y_MARGIN - BOARD_OUTER_LINE_WIDTH,
                              (BLOCK_SIZE + MARGIN_SIZE) * BOARD_WIDTH + BOARD_OUTER_LINE_WIDTH * 2 - MARGIN_SIZE,
                              (BLOCK_SIZE + MARGIN_SIZE) * BOARD_HEIGHT + BOARD_OUTER_LINE_WIDTH * 2 - MARGIN_SIZE)
    # Set Font
    FONT_OBJ = pygame.font.Font('res/fonts/Slate.ttf', FONT_SIZE)
    TITLE_OBJ = pygame.font.Font('res/fonts/PixelOperator-Bold.ttf', TITLE_SIZE)

    main_board = Board()
    title_text = 'Your Score: '
    muted = False

    BG_OBJ = pygame.image.load("res/background.jpg")
    MUTE_OBJ = pygame.image.load("res/unmute.png").convert_alpha()
    UNMUTE_OBJ = pygame.image.load("res/mute.png").convert_alpha()
    BACK_OBJ = pygame.image.load("res/backbutton.png").convert_alpha()

    pygame.display.set_caption('2048 Game for MeAndTheBois™')
    pygame.mixer.music.load('res/music.mp3')
    pygame.mixer.music.play(-1)
    mainmenu()

    # Main game loop
    while True:
        WINDOW.blit(BG_OBJ, (0, 0))
        WINDOW.blit(BACK_OBJ, (20, 20))
        if not muted: WINDOW.blit(MUTE_OBJ, (720, 15))
        else: WINDOW.blit(UNMUTE_OBJ, (720, 15))
        pygame.draw.rect(WINDOW, Color.DeepOrange.value, BLOCK_BOARD, BOARD_OUTER_LINE_WIDTH)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a): main_board.slide(Direction.Left)
                elif event.key in (K_RIGHT, K_d): main_board.slide(Direction.Right)
                elif event.key in (K_UP, K_w): main_board.slide(Direction.Up)
                elif event.key in (K_DOWN, K_s): main_board.slide(Direction.Down)
                elif event.key == K_ESCAPE: mainmenu()

        # Mute/unmute draw_button
        if is_clicked(725, 20, 50, 50):
            pygame.time.wait(100)
            if not muted: pygame.mixer.music.pause()
            else: pygame.mixer.music.unpause()
            muted = not muted

        # Back draw_button (go to main menu)
        if is_clicked(20, 20, 50, 50):
            pygame.time.wait(100)
            mainmenu()

        current_score = main_board.get_max_score()
        draw_blocks(main_board)

        if len(main_board.blocks) >= (BOARD_WIDTH * BOARD_HEIGHT):
            title = 'You Lose! Better luck next time!\n\nHit "Esc" to exit\nor any other key to restart.'
            handle_win_or_lost(Result.Lost, title)
            main_board = Board()
        elif current_score < 2048:
            title = title_text + str(current_score)
            draw_title(title)
        else:
            title = 'Congratulations! You Win!\n\nHit "Esc" to exit\nor any other key to restart.'
            handle_win_or_lost(Result.Win, title)
            main_board = Board()

        pygame.display.update()
        FPS_CLOCK.tick(FPS)

def draw_blocks(board_in):
    for block in board_in.blocks:
        left, top = block_position_to_pixel(block.coordinate_x, block.coordinate_y)
        block_rect_obj = pygame.Rect(left, top, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(WINDOW, COLOR_SWITCHER[block.score], block_rect_obj)
        text_surface_obj = FONT_OBJ.render(str(block.score), True, BOARD_TEXT_COLOR)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = block_rect_obj.center
        WINDOW.blit(text_surface_obj, text_rect_obj)

def block_position_to_pixel(x, y):
    pixel_left = X_MARGIN + (BLOCK_SIZE + MARGIN_SIZE) * x
    pixel_top = Y_MARGIN + (BLOCK_SIZE + MARGIN_SIZE) * y

    return pixel_left, pixel_top

def draw_title(title):
    text_surface_obj = TITLE_OBJ.render(title, True, TEXT_COLOR)
    text_rect_obj = text_surface_obj.get_rect()
    text_rect_obj.center = TITLE_CENTER
    WINDOW.blit(text_surface_obj, text_rect_obj)

def handle_win_or_lost(result, title):
    WINDOW.fill(BACKGROUND_COLOR)
    text_y = Y_MARGIN + int(TITLE_SIZE / 2)
    result_font = pygame.font.Font('res/fonts/Slate.ttf', RESULT_SIZE)

    tokens = title.split('\n')
    text_surface_obj = TITLE_OBJ.render(tokens[0], True, TEXT_COLOR, BACKGROUND_COLOR)
    text_rect_obj = text_surface_obj.get_rect()
    text_rect_obj.top = text_y
    text_rect_obj.centerx = int(WINDOW_WIDTH / 2)
    WINDOW.blit(text_surface_obj, text_rect_obj)
    text_y += RESULT_SIZE

    for text in tokens[1:]:
        text_y += int(RESULT_SIZE * 1.5)
        text_surface_obj = result_font.render(text, True, TEXT_COLOR, BACKGROUND_COLOR)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.top = text_y
        text_rect_obj.centerx = int(WINDOW_WIDTH / 2)
        WINDOW.blit(text_surface_obj, text_rect_obj)

    while True:
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP: return
        pygame.display.update()
        FPS_CLOCK.tick(FPS)

def display_text(text, place, font, colorname, size):
    ''' Function to display text on any surface, provided the co-ordinates, font, size '''
    color = eval('Color.%s.value' % colorname)
    font = pygame.font.Font(font, size)
    text_ =  font.render(text, False, color)
    text_rect = text_.get_rect()
    text_rect.center = place
    WINDOW.blit(text_, text_rect)

def draw_button(text, colorname, x, y, w, h, tx, ty):
    ''' Function to create a button with text in it and set its colour to its light
        version when mouse is hovered on it. Also returns True when clicked on it. '''
    color = eval('Color.%s.value' % colorname)

    pygame.draw.rect(WINDOW, color, [x, y, w, h])
    display_text(text, (tx, ty), "res/fonts/PixelOperator8-Bold.ttf", "Black", 35)

    # Get (x,y) position and clicked draw_button of mouse
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Change draw_button colour to light on mouseover
    if is_hovering(x, y, w, h):
        pygame.draw.rect(WINDOW, eval('Color.%s.value' % ("Light"+colorname)), [x, y, w, h])
        display_text(text, (tx, ty), "res/fonts/PixelOperator8-Bold.ttf", "Black", 35)
    if is_clicked(x, y, w, h): return True

def is_clicked(x, y, w, h):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    for i, j in itertools.product(range(x, x+w+1), range(y, y+h+1)):
        if i == mouse[0] and j == mouse[1] and click[0]: return True

def is_hovering(x, y, w, h):
    mouse = pygame.mouse.get_pos()
    all_coords = [(x,y) for x,y in itertools.product(range(x,x+w), range(y,y+h))]
    if mouse in all_coords: return True

if __name__ == "__main__": game()
