import random
from time import sleep


class Board:
    def __init__(self, height: int) -> None:
        self.height, self.length = height // 2, height * 3
        self.cells: list[list[str]] = self._cells()
        self.player = (-2, 1)
        self.cells[self.player[0]][self.player[1]] = "🛸"
        self.create_castle()

    def _cells(self) -> list[list[str]]:
        return [
            [
                "🔹" if j in [0, self.length - 1] or i in [0, self.height - 1] else "  "
                for j in range(self.length)
            ]
            for i in range(self.height)
        ]

    def move(self, step: int) -> None:
        if step <= self.length - 4:
            for i in range(step):
                self.cells[self.player[0]][self.player[1]] = "  "
                if i == 1:
                    self.player = self.player[0] - 1, self.player[1] + 1
                if i == step - 1:
                    self.player = self.player[0] + 1, self.player[1] + 1
                else:
                    self.player = self.player[0], self.player[1] + 1
                self.cells[self.player[0]][self.player[1]] = "🛸"
                print(self)
                sleep(0.05)
            self._boom()

    def _boom(self) -> None:
        self.cells[self.player[0]][self.player[1]] = "💥"
        print(self)
        sleep(0.3)
        self.cells[self.player[0]][self.player[1]] = "  "
        self.player = self.height - 2, 1
        self.cells[self.player[0]][self.player[1]] = "🛸"
        self.create_castle()
        print(self)

    def create_castle(self) -> None:
        if not any(cell == "🏠" for row in self.cells for cell in row):
            self.cells[self.height - 2][
                random.randint(self.height // 2, self.length - 2)
            ] = "🏠"

    def __str__(self) -> str:
        return "\033[H\033[J" + "\n".join(
            ["".join([str(cell) for cell in rows]) for rows in self.cells]
        )


def run() -> None:
    board = Board(12)
    print(board)

    while True:
        board.move(int(input(f"Insert steps count (1-{board.length - 4}): ")))


if __name__ == "__main__":
    run()
