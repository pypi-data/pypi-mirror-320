import platform
import random


def getch() -> str:
    """Gets a single character"""
    if platform.system() == "Windows":
        import msvcrt

        return str(msvcrt.getch().decode("utf-8")).lower()  # type: ignore
    else:
        import sys
        import termios
        import tty

        fd = sys.stdin.fileno()
        oldsettings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, oldsettings)
        return ch.lower()


def initialize_board(size: int) -> list[list[int]]:
    numbers = list(range(1, size * size)) + [0]  # 0 represents the empty slot
    random.shuffle(numbers)
    return [numbers[i * size : (i + 1) * size] for i in range(size)]


def print_board(board: list[list[int]]) -> None:
    print("\033[H\033[J")
    for row in board:
        print(
            "    ".join(
                f"\033[48;2;50;100;200m{str(num).center(4)}\033[0m"
                if num != 0
                else "    "
                for num in row
            ),
            "\n",
        )

    print("Move the empty tile: w,s,a,d")


def find_empty_tile(board: list[list[int]]) -> tuple[int, int]:
    """Find the position of the empty tile (0)."""
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            if val == 0:
                return r, c
    return 0, 0


def is_valid_move(size: int, row: int, col: int) -> bool:
    return 0 <= row < size and 0 <= col < size


def move_tile(
    board: list[list[int]], empty_pos: tuple[int, int], direction: str
) -> bool:
    """Move a tile into the empty slot if valid."""
    row, col = empty_pos
    if direction == "w":
        target = (row - 1, col)
    elif direction == "s":
        target = (row + 1, col)
    elif direction == "a":
        target = (row, col - 1)
    elif direction == "d":
        target = (row, col + 1)
    elif direction == " ":
        exit()
    else:
        return False

    if is_valid_move(len(board), *target):
        target_row, target_col = target
        board[row][col], board[target_row][target_col] = (
            board[target_row][target_col],
            board[row][col],
        )
        return True
    return False


def is_solved(board: list[list[int]]) -> bool:
    """Check if the puzzle is solved."""
    size = len(board)
    correct = list(range(1, size * size)) + [0]
    flat_board = [num for row in board for num in row]
    return flat_board == correct


def run() -> None:
    board = initialize_board(size=4)

    while not is_solved(board):
        print_board(board)
        if move_tile(board, find_empty_tile(board), getch()):
            if is_solved(board):
                print("Congratulations! You've solved the puzzle!")
                print_board(board)
                break
        else:
            print("Invalid move. Try again.")


if __name__ == "__main__":
    run()
