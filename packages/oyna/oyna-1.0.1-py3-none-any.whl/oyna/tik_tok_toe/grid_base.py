import enum
import math
import platform
import random
import sys
from typing import Literal


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


class Emoji(enum.Enum):
    PLAYER = "❌"
    COMPUTER = "⭕️"
    EMPTY = "  "
    WALL = "🔹"
    WIN = "🥳"
    LOSS = "😂"
    DRAW = "😘"


class Board:
    def __init__(self, size: int) -> None:
        self.game_size = size + 2
        self.player = (self.game_size // 2, self.game_size // 2)
        self.cells = self._cells()
        self.state: Emoji | None = None
        self.memo: dict[tuple[tuple[Emoji, ...], ...], float] = {}

    def _cells(self) -> list[list[Emoji]]:
        return [
            [
                Emoji.WALL
                if j in [0, self.game_size - 1] or i in [0, self.game_size - 1]
                else Emoji.EMPTY
                for j in range(self.game_size)
            ]
            for i in range(self.game_size)
        ]

    def action(self, ch: str) -> None:
        match ch:
            case "w":
                self.player = self.player[0] - 1, self.player[1]
            case "a":
                self.player = self.player[0], self.player[1] - 1
            case "s":
                self.player = self.player[0] + 1, self.player[1]
            case "d":
                self.player = self.player[0], self.player[1] + 1
            case "e":
                if self.cells[self.player[0]][self.player[1]] == Emoji.EMPTY:
                    self.cells[self.player[0]][self.player[1]] = Emoji.PLAYER
                    self.play_game()
            case " ":
                exit()
            case _:
                pass

    def play_game(self) -> None:
        if self.check_winner(Emoji.PLAYER):
            self.state = Emoji.WIN
        else:
            if self.is_full():
                self.state = Emoji.DRAW
            else:
                row, col = self.computer_move()
                self.cells[row][col] = Emoji.COMPUTER
                if self.check_winner(Emoji.COMPUTER):
                    self.state = Emoji.LOSS

    def __str__(self) -> str:
        return "\n".join(
            "".join(
                f"\033[48;2;50;100;200m{self.cells[i][j]}\033[0m"
                if self.player == (i, j)
                else self.cells[i][j].value
                for j in range(self.game_size)
            )
            for i in range(self.game_size)
        )

    def get_empty_cells(self) -> list[tuple[int, int]]:
        return [
            (row, col)
            for row in range(1, self.game_size - 1)
            for col in range(1, self.game_size - 1)
            if self.cells[row][col] == Emoji.EMPTY
        ]

    def is_full(self) -> bool:
        return not self.get_empty_cells()

    def check_winner(self, player: Literal[Emoji.PLAYER, Emoji.COMPUTER]) -> bool:
        for row in self.cells[1:-1]:
            if all(s == player for s in row[1:-1]):
                return True

        for col in range(1, self.game_size - 1):
            if all(
                self.cells[row][col] == player for row in range(1, self.game_size - 1)
            ):
                return True

        if all(self.cells[i][i] == player for i in range(1, self.game_size - 1)):
            return True

        if all(
            self.cells[i][self.game_size - 1 - i] == player
            for i in range(1, self.game_size - 1)
        ):
            return True

        return False

    def minimax(self, is_maximizing: bool, alpha: float, beta: float) -> float:
        board_tuple = tuple(tuple(row) for row in self.cells)
        if board_tuple in self.memo:
            return self.memo[board_tuple]

        if self.check_winner(Emoji.COMPUTER):
            return 1
        if self.check_winner(Emoji.PLAYER):
            return -1
        if self.is_full():
            return 0

        if is_maximizing:
            best = -math.inf
            for row, col in self.get_empty_cells():
                self.cells[row][col] = Emoji.COMPUTER
                best = max(best, self.minimax(False, alpha, beta))
                self.cells[row][col] = Emoji.EMPTY
                alpha = max(alpha, best)
                if beta <= alpha:
                    break  # Pruning
            self.memo[board_tuple] = best
            return best

        else:
            best = math.inf
            for row, col in self.get_empty_cells():
                self.cells[row][col] = Emoji.PLAYER
                best = min(best, self.minimax(True, alpha, beta))
                self.cells[row][col] = Emoji.EMPTY
                beta = min(beta, best)
                if beta <= alpha:
                    break  # Pruning
            self.memo[board_tuple] = best
            return best

    def computer_move(self) -> tuple[int, int]:
        best_move = (-1, -1)
        best_value = -math.inf
        empties = self.get_empty_cells()
        random.shuffle(empties)
        for row, col in empties:
            self.cells[row][col] = Emoji.COMPUTER
            move_value = self.minimax(False, -math.inf, math.inf)
            self.cells[row][col] = Emoji.EMPTY

            if move_value > best_value:
                best_value = move_value
                best_move = (row, col)

        return best_move


def run() -> None:
    board = Board(3)
    while True:
        print(f"\033[H\033[J{board}")
        if board.state is not None:
            print(f"\033[H\033[J{board}")
            print(f"{board.state.name} {board.state}")
            exit()
        board.action(getch())


if __name__ == "__main__":
    run()
