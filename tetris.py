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
next_piece_index = 0

# actual value set in init
piece_move_down_timer = []
piece_move_down_delay = 0.5

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

can_soft_drop = True 
can_soft_drop_timer = [] 
can_hard_drop = True 

# Array of all pieces and all their rotations, stored as offsets in a 4 by 4 grid if an l or O, or a 3 by 3 grid otherwise (follows SRS)
# Additionally, and the 5th value in the list for each piece is the color index, and the 6th is their start position, 7th is piece preview offset in tiles (can be fractional)
pieces = \
[
    [ [ [0, 1], [1, 1], [2, 1], [3, 1] ], [ [2, 0], [2, 1], [2, 2], [2, 3] ], [ [0, 2], [1, 2], [2, 2], [3, 2] ], [ [1, 0], [1, 1], [1, 2], [1, 3] ], 1, [3, 18], [0.5, 1]], # l 
    [ [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], [ [1, 0], [1, 1], [2, 0], [2, 1] ], 2, [3, 18], [0.5, 1.5]], # O
    [ [ [1, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [1, 1], [1, 2], [2, 1] ], [ [0, 1], [1, 1], [2, 1], [1, 2] ], [ [0, 1], [1, 0], [1, 1], [1, 2] ], 3, [3, 19], [1, 1.5]], # T
    [ [ [1, 0], [2, 0], [0, 1], [1, 1] ], [ [1, 0], [1, 1], [2, 1], [2, 2] ], [ [1, 1], [2, 1], [0, 2], [1, 2] ], [ [0, 0], [0, 1], [1, 1], [1, 2] ], 4, [3, 19], [1, 1.5]], # S
    [ [ [0, 0], [1, 0], [1, 1], [2, 1] ], [ [1, 1], [1, 2], [2, 0], [2, 1] ], [ [0, 1], [1, 1], [1, 2], [2, 2] ], [ [0, 1], [0, 2], [1, 0], [1, 1] ], 5, [3, 19], [1, 1.5]], # Z
    [ [ [0, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [2, 0], [1, 1], [1, 2] ], [ [0, 1], [1, 1], [2, 1], [2, 2] ], [ [0, 2], [1, 0], [1, 1], [1, 2] ], 6, [3, 19], [1, 1.5]], # J
    [ [ [2, 0], [0, 1], [1, 1], [2, 1] ], [ [1, 0], [1, 1], [1, 2], [2, 2] ], [ [0, 1], [1, 1], [2, 1], [0, 2] ], [ [0, 0], [1, 0], [1, 1], [1, 2] ], 7, [3, 19], [1, 1.5]]  # L
]

# All game logic initializations go here, so the game can be restarted and such
def init_game():
    global next_piece_index, piece_move_down_timer

    timers.clear()

    create_play_area()
    random.seed()

    next_piece_index = random.randrange(0, 6)

    move_down_timer_length = 0.5
    piece_move_down_timer = [move_down_timer_length, move_down_timer_length, update_piece_pos, False]
    timers.append(piece_move_down_timer)

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
    global can_shift, can_rotate, can_hard_drop
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
                    if can_shift_timer in timers:
                        timers.remove(can_shift_timer)

                if pressed_key == "a" or pressed_key == "b":
                    can_rotate = True

                if pressed_key == "up":
                    can_hard_drop = True

        elif event.type == KEYUP:
            if event.key in input_map:
                released_key = input_map[event.key]
                input_states[released_key] = False

def update(delta):
    global can_shift, can_rotate, can_shift_timer, can_soft_drop, can_soft_drop_timer, can_hard_drop

    for timer in timers:
        update_timer(delta, timer)

    remove_piece_tiles()

    # shifting left and right
    if can_shift:
        shifted = False
        if input_states["right"]:
            piece_attempt_move([1, 0])
            shifted = True
        elif input_states["left"]:
            piece_attempt_move([-1, 0])
            shifted = True

        if shifted:
            can_shift = False
            can_shift_timer = [0.2, 0.2, set_can_shift_true, True]
            timers.append(can_shift_timer)

    # piece rotation
    if can_rotate:
        can_rotate = False 
        if input_states["a"]:
            piece_attempt_rotate((piece_rotation + 1) % 4)
        elif input_states["b"]:
            piece_attempt_rotate((piece_rotation + 3) % 4)

    # soft drops 
    if input_states["down"]:
        piece_move_down_timer[0] = piece_move_down_delay / 4
        if piece_move_down_timer[1] > piece_move_down_timer[0]:
            piece_move_down_timer[1] = piece_move_down_timer[0]
    else:
        piece_move_down_timer[0] = piece_move_down_delay

    # hard drops
    if can_hard_drop and input_states["up"]:
        # this function is needed because we can't break from an inner loop back to an outer loop
        def can_place_piece_at_pos(pos):
            for tile in pieces[piece_index][piece_rotation]:
                collision_occured = tile_collision_check([pos[0] + tile[0], pos[1] + tile[1]])
                if collision_occured:
                    return False
            return True

        can_hard_drop = False

        for row in range(play_area_size[1], piece_pos[1], -1):
            can_place = can_place_piece_at_pos([piece_pos[0], row])
            if can_place:
                piece_pos[1] = row
                lock_piece()
                break

    insert_piece_tiles()
                

# This exists because you can't set variables inside a lambda in python
def set_can_shift_true():
    global can_shift
    can_shift = True 

# lock is needed so the piece cannot lock when inserting a new piece, or else there would be a stack overflow
def update_piece_pos(lock = True):
    global piece_rotation

    remove_piece_tiles()

    piece_moved_down = piece_attempt_move([0, 1])
    if lock and not piece_moved_down:
        lock_piece()
        return

    insert_piece_tiles()
    
def draw():
    screen.fill(pygame.Color(0, 0, 0))

    screen.lock()

    # Drawing tiles in the play area
    for col in range(play_area_size[0]):
        for row in range(int(play_area_size[1] / 2)):
            tile_color_index = play_area[col][row + 20]
            tile_color = colors[tile_color_index]
            pygame.draw.rect(screen, tile_color, [drawn_grid_pos[0] + col * drawn_tile_size[0], drawn_grid_pos[1] + row * drawn_tile_size[1]] + drawn_tile_size)

    # TODO: move this to a separate screen that only gets redrawn once when a new piece is generated
    # next piece preview
    for tile in pieces[next_piece_index][0]:
        tile_color = colors[pieces[next_piece_index][4]]
        tile_preview_offset = pieces[next_piece_index][6]
        tile_x = int(piece_preview_pos[0] + (tile[0] + tile_preview_offset[0]) * drawn_tile_size[0])
        tile_y = int(piece_preview_pos[1] + (tile[1] + tile_preview_offset[1]) * drawn_tile_size[1])
        tile_rect = [tile_x, tile_y] + drawn_tile_size

        pygame.draw.rect(screen, tile_color, tile_rect) # filled color
        pygame.draw.rect(screen, [255, 255, 255], tile_rect, 1) # tile outline

    screen.unlock()

    # Score, Level, and Lines Cleared - TODO

    # despite the name, we're gonna draw the background after everything else
    # this is done so the grid appears on top without using more complicated math for filling the grid with color
    screen.blit(background, [0, 0])

    pygame.display.flip()

def insert_new_piece():
    global piece_index, piece_pos, piece_rotation, next_piece_index

    piece_index = next_piece_index
    next_piece_index = random.randrange(0, 6)
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

def lock_piece():
    insert_piece_tiles()
    attempt_line_clears()
    insert_new_piece()

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
