import itertools
import random
import typing
from enum import Enum


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


class State(Enum):
    BLOCK = "🟪"
    BOMB = "💣"
    DEAD = "💥"
    EIGHT = " 8"
    FIVE = " 5"
    FLAG = "❓"
    FOUR = " 4"
    NINE = " 9"
    ONE = " 1"
    PLAYER = "🟦"
    SEVEN = " 7"
    SIX = " 6"
    THREE = " 3"
    TWO = " 2"
    WALL = "🔹"
    WIN = "🏆"
    ZERO = "  "

    @classmethod
    def create_from_number(cls, number: int) -> "State":
        return {
            0: cls.ZERO,
            1: cls.ONE,
            2: cls.TWO,
            3: cls.THREE,
            4: cls.FOUR,
            5: cls.FIVE,
            6: cls.SIX,
            7: cls.SEVEN,
            8: cls.EIGHT,
            9: cls.NINE,
        }[number]


class Action(Enum):
    CLICK = "click"
    MOVE_DOWN = "down"
    MOVE_LEFT = "left"
    MOVE_RIGHT = "right"
    MOVE_UP = "up"
    SET_FLAG = "flag"


class Cell:
    def __init__(self, state: State = State.BLOCK) -> None:
        self.player_is_here = False
        self.seen = False
        self.state = state
        self.value = 0
        self.down: "Cell"
        self.up: "Cell"
        self.right: "Cell"
        self.left: "Cell"

    def __str__(self) -> str:
        return State.PLAYER.value if self.player_is_here else self.state.value

    def set_neighbors(
        self, left: "Cell", right: "Cell", up: "Cell", down: "Cell"
    ) -> None:
        self.down = down
        self.up = up
        self.right = right
        self.left = left

    def set_state(self, action: Action) -> "Cell":
        match action:
            case Action.SET_FLAG:
                self._set_flag()
                return self
            case Action.CLICK:
                self._click()
                return self
            case _:
                return self._move_tile(action)

    def _move_tile(self, action: Action) -> "Cell":
        side_: "Cell" = getattr(self, action.value)
        if side_.state == State.WALL:
            return self
        else:
            self.player_is_here = False
            side_.player_is_here = True
            return side_

    def _click(self) -> None:
        if self._is_unseen_and_not_wall():
            self.state = (
                State.create_from_number(self.value) if self.value > -1 else State.BOMB
            )
            self.seen = True
            if self._is_empty():
                self._continue(Action.MOVE_DOWN)
                self._continue(Action.MOVE_LEFT)
                self._continue(Action.MOVE_RIGHT)
                self._continue(Action.MOVE_UP)

    def _is_unseen_and_not_wall(self) -> bool:
        return not self.seen and self.state != State.WALL

    def _is_empty(self) -> bool:
        return self.value == 0

    def _set_flag(self) -> None:
        if not self.seen:
            self.state = State.BLOCK if self.state == State.FLAG else State.FLAG

    def _continue(self, side: Action) -> None:
        side_: typing.Union["Cell", None] = getattr(self, side.value)
        if side_ is not None:
            side_.set_state(Action.CLICK)


class Board:
    def __init__(self, size: int) -> None:
        self.start_player_position = size // 2
        self.size = size
        self.cells = self._cells()
        self.set_initial()
        self.player = self.cells[self.start_player_position][self.start_player_position]

    def _cells(self) -> list[list[Cell]]:
        return [[Cell() for _ in range(self.main_size)] for _ in range(self.main_size)]

    @property
    def main_size(self) -> int:
        return self.size + 2

    def set_initial(self) -> None:
        self.set_horizontal_walls()
        self.set_vertical_walls()
        self.set_cells_neighboring()
        self.set_player()
        self.set_bombs()

    def set_horizontal_walls(self) -> None:
        for j in range(self.main_size):
            self.cells[0][j].state = State.WALL
            self.cells[self.main_size - 1][j].state = State.WALL

    def set_vertical_walls(self) -> None:
        for i in range(self.main_size):
            self.cells[i][0].state = State.WALL
            self.cells[i][self.main_size - 1].state = State.WALL

    def set_cells_neighboring(self) -> None:
        for i in range(1, self.main_size - 1):
            for j in range(1, self.main_size - 1):
                self.cells[i][j].set_neighbors(
                    self.cells[i][j - 1],
                    self.cells[i][j + 1],
                    self.cells[i - 1][j],
                    self.cells[i + 1][j],
                )

    def set_player(self) -> None:
        self.cells[self.start_player_position][
            self.start_player_position
        ].player_is_here = True

    def set_bombs(self) -> None:
        for _ in range(self.size + 2):
            cell = self.cells[random.randint(2, self.size - 1)][
                random.randint(2, self.size - 1)
            ]
            if cell.value != -1:
                cell.value = -1
                self.increase_value(cell.down)
                self.increase_value(cell.down.left)
                self.increase_value(cell.down.right)
                self.increase_value(cell.up)
                self.increase_value(cell.up.left)
                self.increase_value(cell.up.right)
                self.increase_value(cell.left)
                self.increase_value(cell.right)

    @staticmethod
    def increase_value(cell: Cell) -> None:
        cell.value += 1 if cell.value != -1 else 0

    def action(self, ch: str) -> None:
        match ch:
            case "w":
                self.player = self.player.set_state(Action.MOVE_UP)
            case "a":
                self.player = self.player.set_state(Action.MOVE_LEFT)
            case "s":
                self.player = self.player.set_state(Action.MOVE_DOWN)
            case "d":
                self.player = self.player.set_state(Action.MOVE_RIGHT)
            case "e":
                self.player = self.player.set_state(Action.CLICK)
            case "q":
                self.player = self.player.set_state(Action.SET_FLAG)
            case " ":
                self.player.state = State.BOMB
            case _:
                pass

    def __str__(self) -> str:
        return "\n".join(["".join([str(cell) for cell in rows]) for rows in self.cells])

    def player_win(self) -> bool:
        for cell in itertools.chain(*self.cells):
            if cell.value >= 0 and cell.state != State.WALL and not cell.seen:
                return False
        return True


class Game:
    def __init__(self) -> None:
        self.board = Board(15)

    def run(self) -> None:
        self._bold_font()
        while self.allow_continue():
            self._print_board()
            self.board.action(getch())
        self.print_result()

    @staticmethod
    def _bold_font() -> None:
        print("\033[1;10m")

    @staticmethod
    def clear_screen() -> None:
        print("\033[H\033[J", end="")

    def _print_board(self) -> None:
        self.clear_screen()
        print(self.board)

    def allow_continue(self) -> bool:
        return self.board.player.state != State.BOMB and not self.board.player_win()

    def print_result(self) -> None:
        for cell in filter(lambda c: c.value < 0, itertools.chain(*self.board.cells)):
            cell.state = State.WIN if self.board.player_win() else State.DEAD
            cell.player_is_here = False
        self._print_board()


def run() -> None:
    Game().run()


if __name__ == "__main__":
    run()
