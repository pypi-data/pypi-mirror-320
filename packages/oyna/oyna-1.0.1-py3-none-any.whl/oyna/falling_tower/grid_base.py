import enum
from time import sleep
from typing import Any, Optional

from pynput import keyboard

user_input: bool = False


class State(enum.Enum):
    BLOCK = "🟪"
    EMPTY = "  "
    WALL = "🔹"


def set_user_input(key: Optional[keyboard.KeyCode | keyboard.Key]) -> None:
    global user_input
    user_input = True or user_input


class Board:
    def __init__(self, size: int) -> None:
        self.size = size + 2
        self.right = True
        self.blocks: list[Any] = [
            self.size - 2,
            [self.size // 3, self.size - self.size // 3],
        ]
        self.player: list[Any] = [2, [self.size // 3, self.size - self.size // 3]]
        self.cells = self._cells()
        self.set_blocks_state()

    def _cells(self) -> list[list[State]]:
        return [
            [
                State.WALL
                if j in [0, self.size - 1] or i in [0, self.size - 1]
                else State.EMPTY
                for j in range(self.size)
            ]
            for i in range(self.size)
        ]

    def set_blocks_state(self) -> None:
        for item in [self.blocks, self.player]:
            for i in range(item[1][0], item[1][1] + 1):
                self.cells[item[0]][i] = State.BLOCK

    def __str__(self) -> str:
        return "\n".join(
            ["".join([cell.value for cell in rows]) for rows in self.cells]
        )

    def update(self) -> None:
        global user_input
        if user_input:
            user_input = False
            self.fall()
            self.clear_player_old_states()
            self.set_blocks_state()
            if self.blocks[0] == 3 or (self.player[1][1] - self.player[1][0]) < 0:
                exit()

        else:
            if self.right:
                self.move_to_right()
            else:
                self.move_to_left()

    def move_to_left(self) -> None:
        if self.player[1][0] == 1:
            self.right = True
        else:
            self.cells[self.player[0]][self.player[1][0] - 1] = State.BLOCK
            self.cells[self.player[0]][self.player[1][1]] = State.EMPTY
            self.player[1][0] -= 1
            self.player[1][1] -= 1

    def move_to_right(self) -> None:
        if self.player[1][1] == self.size - 2:
            self.right = False
        else:
            self.cells[self.player[0]][self.player[1][1] + 1] = State.BLOCK
            self.cells[self.player[0]][self.player[1][0]] = State.EMPTY
            self.player[1][0] += 1
            self.player[1][1] += 1

    def fall(self) -> None:
        self.blocks[0] -= 1
        self.blocks[1] = [
            max([self.blocks[1][0], self.player[1][0]]),
            min([self.blocks[1][1], self.player[1][1]]),
        ]
        self.player[1][0] = self.blocks[1][0]
        self.player[1][1] = self.blocks[1][1]

    def clear_player_old_states(self) -> None:
        for i in range(2, self.size - 1):
            self.cells[self.player[0]][i] = State.EMPTY


def run() -> None:
    keyboard.Listener(on_press=set_user_input).start()
    board = Board(20)
    while True:
        print(f"\033[H\033[J{board}")
        board.update()
        sleep(0.1)


if __name__ == "__main__":
    run()
