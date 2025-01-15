import platform
import random
import sys
from enum import Enum
from time import sleep
from typing import Literal


class Emoji(Enum):
    EMPTY = "🔹"
    VALID_POSITION = "🔸"
    PLAYER = "⚪️"
    COMPUTER = "⚫️"


def getch() -> str:
    """Gets a single character"""
    if platform.system() == "Windows":
        import msvcrt

        return str(msvcrt.getch().decode("utf-8"))  # type: ignore
    else:
        import termios
        import tty

        fd = sys.stdin.fileno()
        oldsettings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, oldsettings)
        return ch


class Board:
    def __init__(self, size: int = 8) -> None:
        self.size = size
        self.cells: list[list[Emoji]] = self._cells()
        self.location = self.size // 2, self.size // 2
        self.initialize()

    def initialize(self) -> None:
        self.cells[3][3], self.cells[4][4] = Emoji.COMPUTER, Emoji.COMPUTER
        self.cells[3][4], self.cells[4][3] = Emoji.PLAYER, Emoji.PLAYER

    def _cells(self) -> list[list[Emoji]]:
        return [[Emoji.EMPTY for _ in range(self.size)] for _ in range(self.size)]

    def print_board(self) -> None:
        board_str = ""
        player_valid_positions = self.get_valid_moves(Emoji.PLAYER)
        for i in range(self.size):
            for j in range(self.size):
                if self.location == (i, j):
                    board_str += f"\033[48;2;50;100;200m{self.cells[i][j].value}\033[0m"
                elif (i, j) in player_valid_positions:
                    board_str += Emoji.VALID_POSITION.value
                else:
                    board_str += self.cells[i][j].value
            board_str += "\n"
        print(f"\033[H\033[J{board_str}")

        if not player_valid_positions:
            print("you dont have any choices, please enter `e` to skip")
            computer_valid_positions = self.get_valid_moves(Emoji.PLAYER)
            if not computer_valid_positions:
                player_count = sum(row.count(Emoji.PLAYER) for row in self.cells)
                computer_count = sum(row.count(Emoji.COMPUTER) for row in self.cells)
                print(f"Score: Player: {player_count}, Computer: {computer_count}")
                exit()

    def is_valid_move(
        self, row: int, col: int, player: Literal[Emoji.PLAYER, Emoji.COMPUTER]
    ) -> bool:
        if self.cells[row][col] != Emoji.EMPTY:
            return False

        opponent = Emoji.COMPUTER if player == Emoji.PLAYER else Emoji.PLAYER
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False

            while (
                0 <= r < self.size
                and 0 <= c < self.size
                and self.cells[r][c] == opponent
            ):
                found_opponent = True
                r += dr
                c += dc

            if (
                found_opponent
                and 0 <= r < self.size
                and 0 <= c < self.size
                and self.cells[r][c] == player
            ):
                return True

        return False

    def get_valid_moves(
        self, player: Literal[Emoji.COMPUTER, Emoji.PLAYER]
    ) -> list[tuple[int, int]]:
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.is_valid_move(r, c, player)
        ]

    def make_move(
        self, row: int, col: int, player: Literal[Emoji.COMPUTER, Emoji.PLAYER]
    ) -> None:
        self.cells[row][col] = player
        opponent = Emoji.COMPUTER if player == Emoji.PLAYER else Emoji.PLAYER
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            path = []

            while (
                0 <= r < self.size
                and 0 <= c < self.size
                and self.cells[r][c] == opponent
            ):
                path.append((r, c))
                r += dr
                c += dc

            if (
                path
                and 0 <= r < self.size
                and 0 <= c < self.size
                and self.cells[r][c] == player
            ):
                for pr, pc in path:
                    self.cells[pr][pc] = player

    def computer_move(self) -> tuple[int, int]:
        return random.choice(self.get_valid_moves(Emoji.COMPUTER))

    def action(self, char: str) -> None:
        move = (0, 0)
        match char:
            case "a":
                move = (0, -1)
            case "d":
                move = (0, 1)
            case "w":
                move = (-1, 0)
            case "s":
                move = (1, 0)
            case " ":
                exit()
            case "e":
                player_valid_moves = self.get_valid_moves(Emoji.PLAYER)
                if player_valid_moves and self.location not in player_valid_moves:
                    return None
                if self.location in player_valid_moves:
                    self.make_move(self.location[0], self.location[1], Emoji.PLAYER)

                sleep(0.3)
                computer_valid_moves = self.get_valid_moves(Emoji.COMPUTER)
                if computer_valid_moves:
                    move = self.computer_move()
                    self.make_move(move[0], move[1], Emoji.COMPUTER)

        new_location = self.location[0] + move[0], self.location[1] + move[1]
        if (
            new_location[0] >= 0
            and new_location[0] < self.size
            and new_location[1] >= 0
            and new_location[1] < self.size
        ):
            self.location = new_location


def run() -> None:
    board = Board()
    while True:
        board.print_board()
        board.action(getch())


if __name__ == "__main__":
    run()
