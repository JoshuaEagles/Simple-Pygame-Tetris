import sys
import pygame
pygame.init()

window_size = [1280, 720]

screen = pygame.display.set_mode(window_size)
background = pygame.Surface(window_size)

play_area = []
play_area_size = [40, 10]

drawn_grid_pos = [480, 40]
drawn_tile_size = [32, 32]
piece_preview_pos = [drawn_grid_pos[0] + (play_area_size[1] + 1) * drawn_tile_size[0], drawn_grid_pos[1]]
piece_preview_size = [drawn_tile_size[0] * 5, drawn_tile_size[1] * 5]
piece_preview_center = piece_preview_pos + [piece_preview_size[0] / 2, piece_preview_size[1] / 2]

colors = [ [0, 0, 0], [0, 206, 241], [255, 213, 0], [145, 56, 167], [114, 203, 59], [255, 50, 19], [3, 65, 174], [255, 151, 28] ]

# Draw Background (to be copied to the main screen every frame)
def create_background():
    for row in range(int(play_area_size[0] / 2)):
        for col in range(play_area_size[1]):
            pygame.draw.rect(background, [255, 255, 255], [drawn_grid_pos[0] + col * drawn_tile_size[0], drawn_grid_pos[1] + row * drawn_tile_size[1]] + drawn_tile_size, 1)
    pygame.draw.rect(background, [255, 255, 255], piece_preview_pos + piece_preview_size, 1)

def create_play_area():
    for row in range(play_area_size[0]):
        play_area.append([])
        for col in range(play_area_size[1]):
            play_area[row].append(0)

def inputs():
    pass 

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
create_play_area()

play_area[35][4] = 1

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    draw()
