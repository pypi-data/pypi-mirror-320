import random
from itertools import permutations


def getch() -> str:
    """Gets a single character"""
    try:
        import msvcrt

        return str(msvcrt.getch().decode("utf-8"))  # type: ignore
    except ImportError:
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
        return ch


class Board:
    def __init__(self, size: int) -> None:
        self.size = size + 2
        self.player = 1, 0
        self.result: list[int] = []
        self.cells = self._cells()
        self.set_values()

    def _cells(self) -> list[list[int]]:
        return [
            [
                -1 if i in [0, self.size - 1] or j in [0, self.size - 1] else 0
                for i in range(self.size)
            ]
            for j in range(self.size)
        ]

    def set_values(self) -> None:
        positions = random.sample(
            list(permutations(range(1, self.size - 2), 2)), k=self.size - 2
        )
        for i, p in enumerate(positions):
            self.cells[p[0]][p[1]] = i + 1

    def action(self, ch: str) -> None:
        match ch:
            case "w":
                if self.cells[self.player[0] - 1][self.player[1]] != -1:
                    self.player = self.player[0] - 1, self.player[1]
            case "a":
                if self.cells[self.player[0]][self.player[1] - 1] != -1:
                    self.player = self.player[0], self.player[1] - 1
            case "s":
                if self.cells[self.player[0] + 1][self.player[1]] != -1:
                    self.player = self.player[0] + 1, self.player[1]
            case "d":
                if self.cells[self.player[0]][self.player[1] + 1] != -1:
                    self.player = self.player[0], self.player[1] + 1
            case "e":
                self.result.append(self.cells[self.player[0]][self.player[1]])
                if len(self.result) == self.size - 2:
                    print("YOU WIN )))")
                    exit()

                if self.result != list(range(1, len(self.result) + 1)):
                    print("YOU LOOSE!!!")
                    exit()
            case " ":
                exit()
            case _:
                pass

    def print_board(self, preview: bool) -> None:
        pr = ""
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) == self.player:
                    pr += "🟦"
                elif self.cells[i][j] == -1:
                    pr += "🔹"
                elif self.cells[i][j] == 0:
                    pr += "🟪"
                else:
                    pr += (
                        str(self.cells[i][j]).center(2)
                        if preview or self.cells[i][j] in self.result
                        else "🟨"
                    )
            pr += "\n"
        print(pr)


def run() -> None:
    board = Board(10)
    board.print_board(True)
    while True:
        print("\033[H\033[J", end="")
        board.action(getch())
        board.print_board(False)


if __name__ == "__main__":
    run()
