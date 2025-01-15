# Shoot color
import enum
import random
from time import sleep
from typing import Literal, Optional

from pynput import keyboard

user_input: Optional[str] = None


class State(enum.Enum):
    EMPTY = "  "
    WALL = "🔹"
    COLOR_RED = "🔴"
    COLOR_BLUE = "🔵"
    COLOR_YELLOW = "🟡"
    COLOR_WHITE = "⚪️"
    COLOR_PURPLE = "🟣"


def colors_state() -> list[State]:
    return [state for state in State if state.name.startswith("COLOR")]


def set_user_input(key: Optional[keyboard.KeyCode | keyboard.Key]) -> None:
    global user_input
    user_input = key.char if isinstance(key, keyboard.KeyCode) else None


class Cell:
    def __init__(self, state: State = State.EMPTY) -> None:
        self.state: State = state
        self.direct: "Cell"
        self.down: "Cell"
        self.up: "Cell"
        self.right: "Cell"
        self.left: "Cell"

    @property
    def opposite(self) -> "Cell":
        if self.direct == self.right:
            return self.left
        elif self.direct == self.left:
            return self.right
        elif self.direct == self.up:
            return self.down
        else:
            return self.up

    def __str__(self) -> str:
        return str(self.state.value)


class Board:
    def __init__(self, size: int) -> None:
        self.player: Cell
        self.size = size + 2 + (size % 2 + 1)
        self.cells = self._cells()
        self.set_cells_neighboring()
        self.set_new_bubble()
        self.set_player()

    def _cells(self) -> list[list[Cell]]:
        return [
            [
                Cell(State.WALL)
                if j in [0, self.size - 1] or i in [0, self.size - 1]
                else Cell(State.EMPTY)
                for j in range(self.size)
            ]
            for i in range(self.size)
        ]

    def set_cells_neighboring(self) -> None:
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                self.cells[i][j].left = self.cells[i][j - 1]
                self.cells[i][j].right = self.cells[i][j + 1]
                self.cells[i][j].up = self.cells[i - 1][j]
                self.cells[i][j].down = self.cells[i + 1][j]
                self.cells[i][j].direct = self._direct(i, j)

    def _direct(self, i: int, j: int) -> Cell:
        if i % 2 == 0:
            return self.cells[i][j].down
        if (i - 1) % 4 == 0 and j == self.size - 2:
            return self.cells[i][j].down
        if (i - 1) % 4 == 2 and j == 1:
            return self.cells[i][j].down
        if (i - 1) % 4 == 0:
            return self.cells[i][j].right
        return self.cells[i][j].left

    def set_player(self) -> None:
        self.player = self.cells[self.size - 2][self.size // 2]
        self.player.state = random.choice(colors_state())

    def set_new_bubble(self) -> None:
        self.cells[1][1].state = random.choice(colors_state())

    def update(self, step: int) -> None:
        match user_input:
            case "a":
                self._move_player("left")
            case "d":
                self._move_player("right")
            case "w":
                shooter = self.player
                while shooter.up.state == State.EMPTY:
                    shooter = shooter.up
                shooter = shooter.up if shooter.up.state != State.WALL else shooter
                self._insert_bubble(shooter, self.player.state)
                if self._matched(shooter):
                    self._clean_bubbles(shooter, shooter.state)

                self._change_player_color()

            case "s":
                self._change_player_color()
        set_user_input(None)
        if step % self.size == 0:
            self._move_bubbles(self.cells[1][1])
            self.set_new_bubble()

    def _change_player_color(self) -> None:
        self.player.state = random.choice(colors_state())

    def _move_bubbles(self, cell: Cell) -> None:
        if cell == self.player:
            exit()
        if cell.state != State.EMPTY:
            self._move_bubbles(cell.direct)
            cell.direct.state = cell.state

    def _move_player(self, side: Literal["left", "right"]) -> None:
        if getattr(self.player, side).state != State.WALL:
            getattr(self.player, side).state = self.player.state
            self.player.state = State.EMPTY
            self.player = getattr(self.player, side)

    def _matched(self, cell: Cell) -> bool:
        return (
            (cell.direct.state == cell.state and cell.opposite.state == cell.state)
            or (
                cell.direct.state == cell.state
                and cell.direct.direct.state == cell.state
            )
            or (
                cell.opposite.state == cell.state
                and cell.opposite.opposite.state == cell.state
            )
        )

    def _clean_bubbles(self, cell: Cell, state: State) -> None:
        cell.state = State.EMPTY
        if cell.direct.state == state:
            self._clean_bubbles(cell.direct, state)

        if cell.opposite.state == state:
            self._clean_bubbles(cell.opposite, state)

    def _insert_bubble(self, cell: Cell, state: State) -> None:
        if cell.state != State.EMPTY:
            self._insert_bubble(cell.direct, cell.state)

        cell.state = state

    def __str__(self) -> str:
        return "\n".join(["".join([str(cell) for cell in rows]) for rows in self.cells])


def run() -> None:
    listener = keyboard.Listener(on_press=set_user_input)
    listener.start()
    board = Board(16)
    step = 0
    while True:
        sleep(0.05)
        board.update(step)
        print(f"\033[H\033[J{board}")
        step += 1


if __name__ == "__main__":
    run()
