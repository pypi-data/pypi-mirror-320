import enum
import itertools
import random
import typing

emojis = [
    "🍰",
    "🍨",
    "🦄",
    "🍀",
    "🍹",
    "🍬",
    "🍁",
    "🍄",
    "🍇",
    "🍓",
    "🍥",
    "🍒",
    "🍭",
    "🍉",
    "🧀",
    "🍩",
    "🌭",
    "🍌",
    "🥥",
    "🐢",
    "🍕",
]


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
    BLOCK = "🟪"
    WALL = "🔹"
    PLAYER = "🟦"
    SOLVED = "🔸"
    WIN = "🏆"


class Side(enum.Enum):
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"


class Cell:
    def __init__(self, state: State = State.BLOCK) -> None:
        self.player_is_here = False
        self.state: State = state
        self.selected: bool = False
        self.value: str = ""
        self.down: "Cell"
        self.up: "Cell"
        self.right: "Cell"
        self.left: "Cell"

    def __str__(self) -> str:
        if self.selected:
            return self.value
        elif self.player_is_here:
            return State.PLAYER.value
        return str(self.state.value)

    def set_neighbors(
        self, left: "Cell", right: "Cell", up: "Cell", down: "Cell"
    ) -> None:
        self.down = down
        self.up = up
        self.right = right
        self.left = left

    def set_player_is_here(self, player_is_here: bool) -> None:
        self.player_is_here = player_is_here

    def set_state(self, state: State) -> None:
        self.state = state

    def move_tile(self, action: Side) -> "Cell":
        side_: "Cell" = getattr(self, action.value)
        if side_.state == State.WALL:
            return self
        else:
            self.player_is_here = False
            side_.player_is_here = True
            return side_


class Board:
    def __init__(self, size: int) -> None:
        self.start_player_position = size // 2
        self.size: int = size + (size % 2)
        self.main_size: int = self.size + 2
        self.cells = self._cells()
        self.set_initial()
        self.selected_tile: typing.Optional[Cell] = None
        self.player = self.cells[self.start_player_position][self.start_player_position]

    def _cells(self) -> list[list[Cell]]:
        return [
            [
                Cell(State.WALL)
                if j in [0, self.main_size - 1] or i in [0, self.main_size - 1]
                else Cell(State.BLOCK)
                for j in range(self.main_size)
            ]
            for i in range(self.main_size)
        ]

    def set_initial(self) -> None:
        self.set_cells_value()
        self.set_cells_neighboring()
        self.set_player()

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
        ].set_player_is_here(True)

    def set_cells_value(self) -> None:
        emoji_needs = divmod(pow(self.size, 2), 2 * len(emojis))
        complete_emojis = emojis * emoji_needs[0]
        extra_emojis = emojis[: emoji_needs[1] // 2]
        emojis_ = 2 * (complete_emojis + extra_emojis)
        random.shuffle(emojis_)
        emoji_cells = filter(
            lambda c: c.state != State.WALL, itertools.chain(*self.cells)
        )
        for i, cell in enumerate(emoji_cells):
            cell.value = emojis_[i]

    def action(self, ch: str) -> None:
        match ch:
            case "w":
                self.player = self.player.move_tile(Side.UP)
            case "a":
                self.player = self.player.move_tile(Side.LEFT)
            case "s":
                self.player = self.player.move_tile(Side.DOWN)
            case "d":
                self.player = self.player.move_tile(Side.RIGHT)
            case "e":
                if self.player.state != State.SOLVED:
                    if self.selected_tile:
                        if self._matched():
                            self._set_selected_tiles_as_solved()
                        else:
                            self._revert_selected_tile()
                    else:
                        self._select_new_tile()
            case " ":
                exit()
            case _:
                pass

    def _select_new_tile(self) -> None:
        self.selected_tile = self.player
        self.selected_tile.selected = True

    def _revert_selected_tile(self) -> None:
        setattr(self.selected_tile, "selected", False)
        self._select_new_tile()

    def _set_selected_tiles_as_solved(self) -> None:
        if self.selected_tile:
            self.selected_tile.state = State.SOLVED
            self.player.state = State.SOLVED
            self.selected_tile.selected = False
        self.selected_tile = None

    def _matched(self) -> bool:
        return (
            getattr(self.selected_tile, "value") == self.player.value
            and self.selected_tile != self.player
        )

    def __str__(self) -> str:
        return "\n".join(["".join(map(str, rows)) for rows in self.cells])

    def player_win(self) -> bool:
        for cell in itertools.chain(*self.cells):
            if cell.state != State.SOLVED and cell.state != State.WALL:
                return False
        self.player.set_state(State.WIN)
        return True


def run() -> None:
    board = Board(8)
    print(f"\033[H\033[J{board}")
    while not board.player_win():
        board.action(getch())
        print(f"\033[H\033[J{board}")


if __name__ == "__main__":
    run()
