# 2048 Game implemented in Python sing PyGame

import pygame, sys, itertools
from pygame import *

# Set of colours (R,G,B)
white = (255, 255, 255)
black = (0,0,0)
light_red = (230, 0, 0)
light_green = (0, 240, 0)
light_blue = (51, 153, 255)
gray = (128, 128, 128)
green = (0, 180, 0)
red = (190, 0, 0)
blue = (0, 102, 204)
fuschia = (255,0,255)
orange = (255,69,0)

# Initialize pygame
pygame.init()
pygame.display.set_caption('2048 Game for MeAndTheBois(TM)')
window = pygame.display.set_mode((800, 600))

def display_text(text, place, font, color, size):
    ''' Function to display text on any surface, provided the co-ordinates, font, size '''
    color = eval(color)
    font = pygame.font.Font(font, size)
    text_ =  font.render(text, False, color)
    text_rect = text_.get_rect()
    text_rect.center = place
    window.blit(text_, text_rect)

def button(text, colorname, x, y, w, h, tx, ty):
    ''' Function to create a button with text in it and set its colour to its light
        version when mouse is hovered on it. Also returns True when clicked on it. '''
    color = eval(colorname)

    pygame.draw.rect(window, color, [x, y, w, h])
    display_text(text, (tx, ty), "res/fonts/PixelOperator8-Bold.ttf", "black", 35)

    # Get (x,y) position and clicked button of mouse
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Detect mouse hover by comparing coordinates of box and mouse point
    for i, j in itertools.product(range(x, x+w+1), range(y, y+h+1)):
        if i == mouse[0] and j == mouse[1]:
            pygame.draw.rect(window, eval("light_"+colorname), [x, y, w, h])
            display_text(text, (tx, ty), "res/fonts/PixelOperator8-Bold.ttf", "black", 35)
            if click[0]: return True

def mainmenu():
    ''' Main Menu of the game '''
    bg = pygame.image.load("res/background.jpg")
    logo = pygame.image.load("res/logo.png").convert_alpha()

    pygame.mixer.music.load('res/mainmenu_music.mp3')
    pygame.mixer.music.play(-1)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: break                 # Quit when the user clicks the exit button
        window.blit(bg, (0, 0))
        window.blit(logo, (215, 75))

        play = button('Play', "green", 335, 200, 165, 60, 410, 230)
        highscore = button('High Scores', "blue", 245, 305, 355, 60, 425, 335)
        quitbutton = button('Quit', "red", 335, 410, 165, 60, 410, 440)

        if quitbutton: break
        #elif play:
            #gameloop()
        #elif highscore:
            #highscores()

        pygame.display.update()

    pygame.quit()
    sys.exit()
mainmenu()
