import enum
import random
from time import sleep
from typing import Optional

from pynput import keyboard


class State(enum.Enum):
    EMPTY = "  "
    BLOCK = "🟪"
    WALL = "🔹"
    PLAYER = "🐣"
    END = "💥"


user_input: bool = False


def set_user_input(key: Optional[keyboard.KeyCode | keyboard.Key]) -> None:
    global user_input
    user_input = True


class Cell:
    def __init__(self, state: State = State.EMPTY) -> None:
        self.state = state
        self.down: "Cell"
        self.up: "Cell"
        self.right: "Cell"
        self.left: "Cell"

    def __str__(self) -> str:
        return str(self.state.value)


class Board:
    def __init__(self, height: int) -> None:
        self.height, self.length = height, height * 4
        self.cells: list[list[Cell]] = self._cells()
        self.player: Cell
        self.set_cells_neighboring()
        self.set_player()

    def _cells(self) -> list[list[Cell]]:
        return [
            [
                Cell(State.WALL)
                if j in [0, self.length - 1] or i in [0, self.height - 1]
                else Cell(State.EMPTY)
                for j in range(self.length)
            ]
            for i in range(self.height)
        ]

    def set_cells_neighboring(self) -> None:
        for i in range(1, self.height - 1):
            for j in range(1, self.length - 1):
                self.cells[i][j].left = self.cells[i][j - 1]
                self.cells[i][j].right = self.cells[i][j + 1]
                self.cells[i][j].up = self.cells[i - 1][j]
                self.cells[i][j].down = self.cells[i + 1][j]

    def set_player(self) -> None:
        self.player = self.cells[1][3]
        self.player.state = State.PLAYER

    def move(self, step: int) -> None:
        self._move_player()
        self._create_new_block(step)
        self._move_block()

    def _move_player(self) -> None:
        global user_input
        self.player.state = State.EMPTY
        self.player = self.player.up if user_input else self.player.down
        self.player.state = (
            State.PLAYER if self.player.state == State.EMPTY else State.END
        )
        user_input = False

    def _create_new_block(self, step: int) -> None:
        if step % 10 == 0 and random.randint(0, 1) == 1:
            for i in range(1, self.height - 1):
                self.cells[i][-2].state = State.BLOCK
            space = random.randint(2, 2 * self.height // 3)
            for i in range(3):
                self.cells[space + i][-2].state = State.EMPTY

    def _move_block(self) -> None:
        for row in self.cells:
            for cell in row:
                if cell.state == State.BLOCK:
                    if cell.left.state == State.PLAYER:
                        self.player.state = State.END
                    else:
                        cell.state = State.EMPTY
                        if cell.left.state != State.WALL:
                            cell.left.state = State.BLOCK

    def __str__(self) -> str:
        return "\033[H\033[J" + "\n".join(
            ["".join([str(cell) for cell in rows]) for rows in self.cells]
        )


def run() -> None:
    board = Board(12)
    listener = keyboard.Listener(on_press=set_user_input)
    listener.start()
    steps = 0
    while board.player.state != State.END:
        sleep(0.2)
        board.move(steps)
        print(f"{board}\n\n\tYour({State.PLAYER.value}) Scores: {steps}")
        steps += 1


if __name__ == "__main__":
    run()
