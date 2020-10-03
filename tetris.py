# TODO: piece preview 
# TODO: level 
# TODO: score and line clear count
import sys
import random
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
    KEYUP,
    SRCALPHA
)
# pylint: enable=no-name-in-module

# pylint: disable=no-member
pygame.init()
# pylint: enable=no-member

window_size = [1280, 720]

screen = pygame.display.set_mode(window_size)
# pylint: disable=too-many-function-args
background = pygame.Surface(window_size, SRCALPHA)
# pylint: enable=too-many-function-args

play_area = []
play_area_size = [10, 40]

drawn_grid_pos = [480, 40]
drawn_tile_size = [32, 32]
piece_preview_pos = [drawn_grid_pos[0] + (play_area_size[0] + 1) * drawn_tile_size[0], drawn_grid_pos[1]]
piece_preview_size = [drawn_tile_size[0] * 5, drawn_tile_size[1] * 5]
piece_preview_center = piece_preview_pos + [piece_preview_size[0] / 2, piece_preview_size[1] / 2]

colors = [ [0, 0, 0], [0, 206, 241], [255, 213, 0], [145, 56, 167], [114, 203, 59], [255, 50, 19], [3, 65, 174], [255, 151, 28] ]

clock = pygame.time.Clock()

# each timer should be a list of 4 items, the first being the wait time, the second will be used as the time left, should be set equal to the wait time 
# the third being the callback fourth if False makes the timer an interval (doesn't expire)
timers = []

# variables for the currently moving piece
piece_pos = [0, 0] # relative to the play area
piece_index = 0
piece_rotation = 0

input_states = \
{
    "left" : False,
    "right" : False,
    "up" : False,
    "down" : False,
    "a" : False,
    "b" : False,
    "pause" : False
}

# Translate the integer key IDs into the readable strings using this dictionary (can also rebind actions here)
input_map = \
{
    K_a : "left",
    K_d : "right",
    K_w : "up",
    K_s : "down",
    K_k : "a",
    K_j : "b",
    K_RETURN : "pause",
}

# can_shift set to false means you can't move left or right, can_rotate set to false means you can't rotate
# the timers are just for pointers that get set when the timers are created
can_shift = True 
can_shift_timer = []
can_rotate = True
can_rotate_timer = []

# Array of all pieces and all their rotations, stored as offsets in a 4 by 4 grid if an l or O, or a 3 by 3 grid otherwise (follows SRS)
# Additionally, and the 5th value in the list for each piece is the color index, and the 6th is their start position
pieces = \
[
    [ [ [0, 1], [1, 1], [2, 1], [3, 1] ], [ [2, 0], [2, 1], [2, 2], [2, 3] ], [ [0, 2], [1, 2], [2, 2], [3, 2] ], [ [1, 0], [1, 1], [1, 2], [1, 3] ], 1, [3, 18] ], # l 
    [ [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], 2, [4, 18]], # O
    [ [ [1, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [1, 1], [1, 2], [2, 1] ], [ [0, 1], [1, 1], [2, 1], [1, 2] ], [ [0, 1], [1, 0], [1, 1], [1, 2] ], 3, [3, 19]], # T
    [ [ [1, 0], [2, 0], [0, 1], [1, 1] ], [ [1, 0], [1, 1], [2, 1], [2, 2] ], [ [1, 1], [2, 1], [0, 2], [1, 2] ], [ [0, 0], [0, 1], [1, 1], [1, 2] ], 4, [3, 19]], # S
    [ [ [0, 0], [1, 0], [1, 1], [2, 1] ], [ [1, 1], [1, 2], [2, 0], [2, 1] ], [ [0, 1], [1, 1], [1, 2], [2, 2] ], [ [0, 1], [0, 2], [1, 0], [1, 1] ], 5, [3, 19]], # Z
    [ [ [0, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [2, 0], [1, 1], [1, 2] ], [ [0, 1], [1, 1], [2, 1], [2, 2] ], [ [0, 2], [1, 0], [1, 1], [1, 2] ], 6, [3, 19]], # J
    [ [ [2, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [1, 1], [1, 2], [2, 2] ], [ [0, 1], [1, 1], [2, 1], [0, 2] ], [ [0, 0], [1, 0], [1, 1], [1, 2] ], 7, [3, 19]]  # L
]

# All game logic initializations go here, so the game can be restarted and such
def init_game():
    create_play_area()
    random.seed()

    insert_new_piece()

# Draw Background (to be copied to the main screen every frame)
def create_background():
    background.fill([0, 0, 0, 0])
    background.lock()
    for col in range(play_area_size[0]):
        for row in range(int(play_area_size[1] / 2)):
            pygame.draw.rect(background, [255, 255, 255], [drawn_grid_pos[0] + col * drawn_tile_size[0], drawn_grid_pos[1] + row * drawn_tile_size[1]] + drawn_tile_size, 1)
    pygame.draw.rect(background, [255, 255, 255], piece_preview_pos + piece_preview_size, 1)
    background.unlock()

def create_play_area():
    for col in range(play_area_size[0]):
        play_area.append([])
        for _row in range(play_area_size[1]):
            play_area[col].append(0)

def event_handler():
    global can_shift, can_rotate
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN: 
            if event.key in input_map:
                pressed_key = input_map[event.key]
                input_states[pressed_key] = True

                # if i had a just pressed system, this code could go elsewhere
                if pressed_key == "right" or pressed_key == "left":
                    can_shift = True
                    timers.remove(can_shift_timer)
                if pressed_key == "a" or pressed_key == "b":
                    can_rotate = True

        elif event.type == KEYUP:
            if event.key in input_map:
                released_key = input_map[event.key]
                input_states[released_key] = False

def update(delta):
    global can_shift, can_rotate, can_shift_timer, can_rotate_timer

    for timer in timers:
        update_timer(delta, timer)

    remove_piece_tiles()
    if can_shift:
        if input_states["right"] and can_shift:
            piece_attempt_move([1, 0])
        elif input_states["left"] and can_shift:
            piece_attempt_move([-1, 0])
        can_shift = False 
        can_shift_timer = [0.2, 0.2, set_can_shift_true, True]
        timers.append(can_shift_timer)
    if can_rotate:
        if input_states["a"] and can_rotate:
            piece_attempt_rotate((piece_rotation + 1) % 4)
        elif input_states["b"] and can_rotate:
            piece_attempt_rotate((piece_rotation + 3) % 4)
        can_rotate = False 
    insert_piece_tiles()

# This exists because you can't set variables inside a lambda in python
def set_can_shift_true():
    global can_shift
    can_shift = True 

def update_piece_pos(lock = True):
    global piece_rotation

    remove_piece_tiles()

    piece_moved_down = piece_attempt_move([0, 1])
    if lock and not piece_moved_down:
        insert_piece_tiles()
        attempt_line_clears()
        insert_new_piece()
        return

    insert_piece_tiles()
    timers.append([0.25, 0.25, update_piece_pos, True])
    
def draw():
    screen.fill(pygame.Color(0, 0, 0))

    # Drawing tiles at their location
    screen.lock()
    for col in range(play_area_size[0]):
        for row in range(int(play_area_size[1] / 2)):
            tile_color_index = play_area[col][row + 20]
            tile_color = colors[tile_color_index]
            pygame.draw.rect(screen, tile_color, [drawn_grid_pos[0] + col * drawn_tile_size[0], drawn_grid_pos[1] + row * drawn_tile_size[1]] + drawn_tile_size)
    screen.unlock()

    # Piece Preview - TODO

    # Score, Level, and Lines Cleared - TODO

    # despite the name, we're gonna draw the background after everything else
    # this is done so the grid appears on top without using more complicated math for filling the grid with color
    screen.blit(background, [0, 0])

    pygame.display.flip()

def insert_new_piece():
    global piece_index, piece_pos, piece_rotation

    piece_index = random.randrange(0, 6)
    piece_pos = pieces[piece_index][5].copy()
    piece_rotation = 0

    insert_piece_tiles()
    update_piece_pos(False)

# insert tiles for the current piece so it displays on the grid
def insert_piece_tiles():
    for tile in pieces[piece_index][piece_rotation]:
        play_area[piece_pos[0] + tile[0]][piece_pos[1] + tile[1]] = pieces[piece_index][4]
    
# remove tiles for the current piece so it can be moved
def remove_piece_tiles():
    for tile in pieces[piece_index][piece_rotation]:
        play_area[piece_pos[0] + tile[0]][piece_pos[1] + tile[1]] = 0

def update_timer(delta, timer):
    timer[1] -= delta 
    if timer[1] <= 0:
        timer[2]()
        if timer[3]:
            timers.remove(timer)
        else: 
            timer[1] = timer[0]

# returns true if the move was successful
def piece_attempt_move(move_dir):
    for tile in pieces[piece_index][piece_rotation]:
        if tile_collision_check([piece_pos[0] + tile[0] + move_dir[0], piece_pos[1] + tile[1] + move_dir[1]]):
            return False
    piece_pos[0] = piece_pos[0] + move_dir[0]
    piece_pos[1] = piece_pos[1] + move_dir[1]
    return True

# returns true if the rotation was successful
def piece_attempt_rotate(new_rotation):
    global piece_rotation
    for tile in pieces[piece_index][new_rotation]:
        if tile_collision_check([piece_pos[0] + tile[0], piece_pos[1] + tile[1]]):
            return False
    piece_rotation = new_rotation 
    return True
    
# returns true if a collision occured
def tile_collision_check(tile_pos):
    # if out of bounds or the tile in the play area isn't empty, we have collided
    if tile_pos[0] > play_area_size[0] - 1 or tile_pos[0] < 0 or tile_pos[1] > play_area_size[1] - 1 or tile_pos[1] < 0:
        return True
    return play_area[tile_pos[0]][tile_pos[1]] != 0

# called when locking a piece, checks for line clears, and clears them if found
def attempt_line_clears():
    # to make sure we clear lines from the top down and only check for clears once per row, add only distinct row positions to an array and sort them
    rows_to_check = []

    for tile_pos in pieces[piece_index][piece_rotation]:
        if tile_pos[1] not in rows_to_check:
            rows_to_check.append(tile_pos[1])
    rows_to_check.sort()

    def check_if_row_filled(row):
        for col in range(play_area_size[0]):
            if play_area[col][row + piece_pos[1]] == 0: 
                return
            elif col == play_area_size[0] - 1: # at the end of the column and no empty tiles
                shift_play_area_down(row + piece_pos[1])

    for row in rows_to_check:
        check_if_row_filled(row)

# this shifts all the tiles above a specified row down 1 tile
# index 39 is the very bottom of the play area
def shift_play_area_down(cleared_row):
    for col in range(play_area_size[0]):
        for row in range(cleared_row, 0, -1):
            play_area[col][row] = play_area[col][row - 1]

create_background()

init_game()

# Main loop
while True:
    delta = clock.get_time() / 1000 # delta in seconds

    event_handler()

    update(delta)

    draw()

    clock.tick(60)
