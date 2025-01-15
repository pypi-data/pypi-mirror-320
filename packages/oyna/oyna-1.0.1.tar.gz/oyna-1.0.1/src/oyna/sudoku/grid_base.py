import enum
import random
from random import sample
from typing import Optional


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


class State(enum.Enum):
    EMPTY = "  "
    PLAYER = "🟦"
    INTERNAL_WALL = "🔹"
    EXTERNAL_WALL = "🔸"
    FIXED_NUMBER = ""
    END = "🟩"


class Action(enum.Enum):
    MOVE_DOWN = "down"
    MOVE_LEFT = "left"
    MOVE_RIGHT = "right"
    MOVE_UP = "up"
    EXIT = "exit"
    NOTHING = "nothing"
    INSERT_ONE = 1
    INSERT_TWO = 2
    INSERT_THREE = 3
    INSERT_FOUR = 4
    INSERT_FIVE = 5
    INSERT_SIX = 6
    INSERT_SEVEN = 7
    INSERT_EIGHT = 8
    INSERT_NINE = 9


class Cell:
    def __init__(self, state: State = State.EMPTY, value: int = -1) -> None:
        self.player_is_here: bool = False
        self.state: State = state
        self.value: int = value
        self.user_value: Optional[int] = None
        self.down: "Cell"
        self.up: "Cell"
        self.right: "Cell"
        self.left: "Cell"

    def __str__(self) -> str:
        match self:
            case self if self.player_is_here:
                v = (
                    self.value
                    if self.state == State.FIXED_NUMBER
                    else self.user_value or "  "
                )
                return f"\033[48;2;50;100;200m{v:2}\033[0m"
            case self if self.state == State.FIXED_NUMBER:
                return f"{self.value:2}"
            case self if self.state == State.EMPTY and self.user_value is not None:
                color = "\033[92m" if self.value == self.user_value else "\033[91m"
                return f"{color}{self.user_value:2}\033[0m"
            case _:
                return str(self.state.value)

    def take(self, action: Action) -> "Cell":
        match action:
            case Action.EXIT:
                self.state = State.END
                return self

            case move if move in [
                Action.MOVE_DOWN,
                Action.MOVE_RIGHT,
                Action.MOVE_UP,
                Action.MOVE_LEFT,
            ]:
                return self.move_tile(move)
            case Action.NOTHING:
                return self
            case _:
                return self.enter(action)

    def enter(self, action: Action) -> "Cell":
        if self.state == State.EMPTY:
            self.user_value = action.value
        return self

    def move_tile(self, action: Action) -> "Cell":
        side: "Cell" = getattr(self, action.value)
        if side.state == State.EXTERNAL_WALL:
            return self
        elif side.state == State.INTERNAL_WALL:
            side_side: "Cell" = getattr(side, action.value)
            side_side.player_is_here = True
            self.player_is_here = False
            return side_side
        else:
            self.player_is_here = False
            side.player_is_here = True
            return side


class Board:
    def __init__(self) -> None:
        self.size = 3
        self.width = self.size**2 + self.size + 1
        self.cells: list[list[Cell]]
        self.player: Cell
        self.set_up()

    def set_up(self) -> None:
        self.set_cells()
        self.set_walls()
        self.set_cells_neighboring()
        self.set_numbers()
        self.set_player()

    def set_cells(self) -> None:
        self.cells = [[Cell() for _ in range(self.width)] for _ in range(self.width)]

    def set_walls(self) -> None:
        for i in range(self.width - 1):
            for j in [0, self.width - 1]:
                self.cells[i][j].state = State.EXTERNAL_WALL
                self.cells[j][i].state = State.EXTERNAL_WALL

            for j in range(self.size + 1, self.width - self.size, self.size + 1):
                self.cells[i][j].state = State.INTERNAL_WALL
                self.cells[j][i].state = State.INTERNAL_WALL

        self.cells[self.width - 1][self.width - 1].state = State.EXTERNAL_WALL

    def set_cells_neighboring(self) -> None:
        for i in range(1, self.width - 1):
            for j in range(1, self.width - 1):
                self.cells[i][j].left = self.cells[i][j - 1]
                self.cells[i][j].right = self.cells[i][j + 1]
                self.cells[i][j].up = self.cells[i - 1][j]
                self.cells[i][j].down = self.cells[i + 1][j]

    def set_player(self) -> None:
        self.player = self.cells[1][1]
        self.player.player_is_here = True

    def set_numbers(self) -> None:
        side = self.size * self.size

        def pattern(r: int, c: int) -> int:
            return (self.size * (r % self.size) + r // self.size + c) % side

        def shuffle(s: range) -> list[int]:
            return sample(s, len(s))

        rBase = range(self.size)
        rows = [g * self.size + r for g in shuffle(rBase) for r in shuffle(rBase)]
        cols = [g * self.size + c for g in shuffle(rBase) for c in shuffle(rBase)]
        nums = shuffle(range(1, self.size * self.size + 1))

        numbers = [[nums[pattern(r, c)] for c in cols] for r in rows]
        for i, row in enumerate(numbers):
            for j, value in enumerate(row):
                i_ = i + i // self.size + 1
                j_ = j + j // self.size + 1
                self.cells[i_][j_].value = value
                self.cells[i_][j_].state = (
                    State.EMPTY if random.randint(0, 7) > 2 else State.FIXED_NUMBER
                )

    def take(self, ch: str) -> None:
        self.player = self.player.take(
            {
                "w": Action.MOVE_UP,
                "a": Action.MOVE_LEFT,
                "s": Action.MOVE_DOWN,
                "d": Action.MOVE_RIGHT,
                " ": Action.EXIT,
                "1": Action.INSERT_ONE,
                "2": Action.INSERT_TWO,
                "3": Action.INSERT_THREE,
                "4": Action.INSERT_FOUR,
                "5": Action.INSERT_FIVE,
                "6": Action.INSERT_SIX,
                "7": Action.INSERT_SEVEN,
                "8": Action.INSERT_EIGHT,
                "9": Action.INSERT_NINE,
            }.get(ch, Action.NOTHING)
        )

    def __str__(self) -> str:
        return "\n".join(["".join(map(str, rows)) for rows in self.cells])


def run() -> None:
    board = Board()
    print(f"\033[H\033[J{board}")
    while board.player.state != State.END:
        board.take(getch())
        print(f"\033[H\033[J{board}")


if __name__ == "__main__":
    run()
