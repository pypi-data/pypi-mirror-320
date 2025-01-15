import random
import time

from pynput import keyboard

# Game configuration
WIDTH, HEIGHT = 20, 20

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
]

# Initialize game board
board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Current tetromino state
current_shape = random.choice(SHAPES)
current_x, current_y = WIDTH // 2 - 1, 0

# Game state
game_over = False


def draw_board() -> None:
    temp_board = [row[:] for row in board]

    for i, row in enumerate(current_shape):
        for j, cell in enumerate(row):
            if cell and current_y + i < HEIGHT and current_x + j < WIDTH:
                temp_board[current_y + i][current_x + j] = cell
    print("\033[H\033[J")
    for row in temp_board:
        print("🔹" + "".join("🟪" if cell else "  " for cell in row) + "🔹")
    print("🔹" + "🔹" * WIDTH + "🔹")


def can_place(shape: list[list[int]], x: int, y: int) -> bool:
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if (
                    x + j < 0
                    or x + j >= WIDTH
                    or y + i >= HEIGHT
                    or board[y + i][x + j]
                ):
                    return False
    return True


def place_tetromino(shape: list[list[int]], x: int, y: int) -> None:
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                board[y + i][x + j] = 1


def clear_lines() -> None:
    global board
    board = [row for row in board if any(cell == 0 for cell in row)]
    while len(board) < HEIGHT:
        board.insert(0, [0 for _ in range(WIDTH)])


def move_left() -> None:
    global current_x
    if can_place(current_shape, current_x - 1, current_y):
        current_x -= 1


def move_right() -> None:
    global current_x
    if can_place(current_shape, current_x + 1, current_y):
        current_x += 1


def rotate() -> None:
    global current_shape
    rotated = [list(row) for row in zip(*current_shape[::-1])]
    if can_place(rotated, current_x, current_y):
        current_shape = rotated


def drop() -> None:
    global current_y, current_shape, current_x, game_over
    if can_place(current_shape, current_x, current_y + 1):
        current_y += 1
    else:
        place_tetromino(current_shape, current_x, current_y)
        clear_lines()
        current_shape = random.choice(SHAPES)
        current_x, current_y = WIDTH // 2 - 1, 0
        if not can_place(current_shape, current_x, current_y):
            game_over = True


def on_press(key: keyboard.KeyCode) -> None:
    try:
        if key.char == "a":
            move_left()
        elif key.char == "d":
            move_right()
        elif key.char == "w":
            rotate()
        elif key.char == "s":
            drop()
    except AttributeError:
        pass


def run() -> None:
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while not game_over:
        draw_board()
        time.sleep(0.2)
        drop()
    print("Game Over!")


if __name__ == "__main__":
    run()
