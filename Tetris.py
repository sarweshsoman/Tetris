import pygame
import random
from pygame.locals import *

# Constants
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE
FPS = 30
START_SPEED = 0.5
SPEED_INCREASE_AMOUNT = 0.1
SPEED_INCREASE_INTERVAL = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_GREY = (50, 50, 50)

# Tetrominoes
tetrominoes = [
    [[1, 1, 1, 1]],  # I shape
    [[1, 1, 1], [0, 1, 0]],  # T shape
    [[1, 1, 0], [0, 1, 1]],  # Squigly shape
    [[0, 1, 1], [1, 1, 0]],  # Reverse Squigly shape
    [[1, 1, 1], [1, 0, 0]],  # L shape
    [[1, 1], [1, 1]]  # Box shape
    # Add more shapes here
]

# Initialize Pygame
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def draw_block(x, y, color):
    pygame.draw.rect(win, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(win, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2)

def new_piece():
    piece = random.choice(tetrominoes)
    color = random.choice([RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE])
    return {'shape': piece, 'color': color, 'x': GRID_WIDTH // 2 - len(piece[0]) // 2, 'y': 0}

def valid_position(board, piece, off_x=0, off_y=0):
    shape = piece['shape']
    for y, row in enumerate(shape):
        for x, val in enumerate(row):
            if val:
                pos_x = piece['x'] + x + off_x
                pos_y = piece['y'] + y + off_y
                if pos_x < 0 or pos_x >= GRID_WIDTH or pos_y >= GRID_HEIGHT:
                    return False
                if pos_y >= 0 and board[pos_y][pos_x]:
                    return False
    return True

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def merge_piece(board, piece):
    shape = piece['shape']
    for y, row in enumerate(shape):
        for x, val in enumerate(row):
            if val:
                board[piece['y'] + y][piece['x'] + x] = piece['color']

def remove_completed_lines(board):
    lines_to_remove = []
    for i, row in enumerate(board):
        if all(row):
            lines_to_remove.append(i)

    for row_idx in lines_to_remove:
        del board[row_idx]
        board.insert(0, [0 for _ in range(GRID_WIDTH)])
def draw_board(board):
    for y, row in enumerate(board):
        for x, val in enumerate(row):
            if val:
                draw_block(x, y, val)
    
    # Add random white dots
    for _ in range(200):  # Adjust the number of dots as needed
        rand_x = random.randint(0, GRID_WIDTH - 1)
        rand_y = random.randint(0, GRID_HEIGHT - 1)
        if board[rand_y][rand_x] == 0:  # Check if the spot is empty
            pygame.draw.rect(win, WHITE, (rand_x * BLOCK_SIZE, rand_y * BLOCK_SIZE, 2, 2))


def main():
    board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    falling_piece = new_piece()
    fall_speed = START_SPEED
    placed_tetrominoes = 0
    game_over = False
    paused = False
    new_game = False
    restart_timer = 0

    overlay_surface = pygame.Surface((WIDTH, HEIGHT))
    overlay_surface.set_alpha(128)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                elif event.key == pygame.K_n:
                    new_game = True
                elif not game_over:
                    if event.key == pygame.K_LEFT:
                        if valid_position(board, falling_piece, off_x=-1):
                            falling_piece['x'] -= 1
                    elif event.key == pygame.K_RIGHT:
                        if valid_position(board, falling_piece, off_x=1):
                            falling_piece['x'] += 1
                    elif event.key == pygame.K_UP:
                        rotated_piece = rotate(falling_piece['shape'])
                        if valid_position(board, {'shape': rotated_piece, 'x': falling_piece['x'], 'y': falling_piece['y']}):
                            falling_piece['shape'] = rotated_piece
                    elif event.key == pygame.K_DOWN:
                        while valid_position(board, falling_piece, off_y=1):
                            falling_piece['y'] += 1

        if new_game:
            board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            falling_piece = new_piece()
            fall_speed = START_SPEED
            placed_tetrominoes = 0
            game_over = False
            new_game = False
            paused = False
            restart_timer = 0

        if not paused and not game_over:
            if valid_position(board, falling_piece, off_y=1):
                falling_piece['y'] += 1
            else:
                merge_piece(board, falling_piece)
                remove_completed_lines(board)
                placed_tetrominoes += 1
                if placed_tetrominoes % SPEED_INCREASE_INTERVAL == 0:
                    fall_speed -= SPEED_INCREASE_AMOUNT
                    if fall_speed < 0:
                        fall_speed = 0

                falling_piece = new_piece()

                for x, val in enumerate(board[0]):
                    if val:
                        game_over = True
                        break

        if game_over:
            restart_timer += clock.get_rawtime()

            if restart_timer >= 2000:
                new_game = True
                restart_timer = 0

        win.fill(BLACK)
        draw_board(board)

        if paused:
            font = pygame.font.Font(None, 36)
            text = font.render('Paused', True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            win.blit(text, text_rect)

        if game_over:
            overlay_surface.fill((0, 0, 0))
            win.blit(overlay_surface, (0, 0))

            font = pygame.font.Font(None, 48)
            text = font.render('Game Over', True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            win.blit(text, text_rect)

        for y, row in enumerate(falling_piece['shape']):
            for x, val in enumerate(row):
                if val:
                    draw_block(falling_piece['x'] + x, falling_piece['y'] + y, falling_piece['color'])

        pygame.display.flip()
        clock.tick(FPS)
        pygame.time.delay(int(1000 * fall_speed))

    pygame.quit()

if __name__ == "__main__":
    main()
