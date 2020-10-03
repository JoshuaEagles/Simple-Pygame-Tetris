import sys
import pygame
# pylint: disable=no-name-in-module
from pygame.locals import (
    K_a, 
    K_d, 
    K_w, 
    K_s, 
    K_k, 
    K_j, 
    K_RETURN,
    QUIT,
    KEYDOWN,
    KEYUP
)
# pylint: enable=no-name-in-module

# pylint: disable=no-member
pygame.init()
# pylint: enable=no-member

window_size = [1280, 720]

screen = pygame.display.set_mode(window_size)
# pylint: disable=too-many-function-args
background = pygame.Surface(window_size)
# pylint: enable=too-many-function-args

play_area = []
play_area_size = [40, 10]

drawn_grid_pos = [480, 40]
drawn_tile_size = [32, 32]
piece_preview_pos = [drawn_grid_pos[0] + (play_area_size[1] + 1) * drawn_tile_size[0], drawn_grid_pos[1]]
piece_preview_size = [drawn_tile_size[0] * 5, drawn_tile_size[1] * 5]
piece_preview_center = piece_preview_pos + [piece_preview_size[0] / 2, piece_preview_size[1] / 2]

colors = [ [0, 0, 0], [0, 206, 241], [255, 213, 0], [145, 56, 167], [114, 203, 59], [255, 50, 19], [3, 65, 174], [255, 151, 28] ]

fps_cap_clock = pygame.time.Clock()

# First bool is "is key pressed", second is "is key just pressed", second will update to false 1/60 of a second after the key is pressed
# For now, just_pressed goes unused
input_states = \
{
    "Left" : { "pressed": False, "just_pressed": False }, # Left
    "Right" : { "pressed": False, "just_pressed": False }, # Right
    "Up" : { "pressed": False, "just_pressed": False }, # Up
    "Down" : { "pressed": False, "just_pressed": False }, # Down
    "A" : { "pressed": False, "just_pressed": False }, # A
    "B" : { "pressed": False, "just_pressed": False }, # B
    "Pause" : { "pressed": False, "just_pressed": False }  # Pause
}

# Translate the integer key IDs into the readable strings using this dictionary (can also rebind actions here)
input_map = \
{
    K_a : "Left",
    K_d : "Right",
    K_w : "Up",
    K_s : "Down",
    K_k : "A",
    K_j : "B",
    K_RETURN : "Pause",
}

# Array of all pieces and all their rotations, stored as offsets in a 4 by 4 grid if an l or O, or a 3 by 3 grid otherwise (follows SRS)
# Additionally, the 5th value in the list for each piece is the color index
pieces = \
[
    [ [ [0, 1], [1, 1], [2, 1], [3, 1] ], [ [2, 0], [2, 1], [2, 2], [2, 3] ], [ [0, 2], [1, 2], [2, 2], [3, 2] ], [ [1, 0], [1, 1], [1, 2], [1, 3] ], 1 ], # l 
    [ [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], 2 ], # O
    [ [ [1, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [1, 1], [1, 2], [2, 1] ], [ [0, 1], [1, 1], [2, 1], [1, 2] ], [ [0, 1], [1, 0], [1, 1], [1, 2] ], 3 ], # T
    [ [ [1, 0], [2, 0], [0, 1], [1, 1] ], [ [1, 0], [1, 1], [2, 1], [2, 2] ], [ [1, 1], [2, 1], [0, 2], [1, 2] ], [ [0, 0], [0, 1], [1, 1], [1, 2] ], 4 ], # S
    [ [ [0, 0], [1, 0], [1, 1], [2, 1] ], [ [1, 1], [1, 2], [2, 0], [2, 1] ], [ [0, 1], [1, 1], [1, 2], [2, 2] ], [ [0, 1], [0, 2], [1, 0], [1, 1] ], 5 ], # Z
    [ [ [0, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [2, 0], [1, 1], [1, 2] ], [ [0, 1], [1, 1], [2, 1], [2, 2] ], [ [0, 2], [1, 0], [1, 1], [1, 2] ], 6 ], # J
    [ [ [2, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [1, 1], [1, 2], [2, 2] ], [ [0, 1], [1, 1], [2, 1], [0, 2] ], [ [0, 0], [1, 0], [1, 1], [1, 2] ], 7 ]  # L
]

# All game logic initializations go here, so the game can be restarted and such
def init_game():
    create_play_area()

# Draw Background (to be copied to the main screen every frame)
def create_background():
    for row in range(int(play_area_size[0] / 2)):
        for col in range(play_area_size[1]):
            pygame.draw.rect(background, [255, 255, 255], [drawn_grid_pos[0] + col * drawn_tile_size[0], drawn_grid_pos[1] + row * drawn_tile_size[1]] + drawn_tile_size, 1)
    pygame.draw.rect(background, [255, 255, 255], piece_preview_pos + piece_preview_size, 1)

def create_play_area():
    for row in range(play_area_size[0]):
        play_area.append([])
        for _col in range(play_area_size[1]):
            play_area[row].append(0)

def event_handler():
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in input_map:
                pressed_key = input_map[event.key]
                input_states[pressed_key]["pressed"] = True
        elif event.type == KEYUP:
            if event.key in input_map:
                released_key = input_map[event.key]
                input_states[released_key]["pressed"] = False

def update():
    pass 

def draw():
    screen.fill(pygame.Color(0, 0, 0))

    # Drawing tiles at their location
    for row in range(int(play_area_size[0] / 2)):
        for col in range(play_area_size[1]):
            tile_color_index = play_area[row + 20][col]
            tile_color = colors[tile_color_index]
            if tile_color_index == 0:
                continue
            else: 
                pygame.draw.rect(background, tile_color, [drawn_grid_pos[0] + col * drawn_tile_size[0], drawn_grid_pos[1] + row * drawn_tile_size[1]] + drawn_tile_size)

    # Piece Preview - TODO

    # Score, Level, and Lines Cleared - TODO

    # despite the name, we're gonna draw the background after everything else
    # this is done so the grid appears on top without using more complicated math for filling the grid with color
    screen.blit(background, [0, 0])

    pygame.display.flip()

create_background()

init_game()

play_area[20][4] = 1

# Main loop
while True:
    event_handler()

    update()

    draw()

    fps_cap_clock.tick(60)
