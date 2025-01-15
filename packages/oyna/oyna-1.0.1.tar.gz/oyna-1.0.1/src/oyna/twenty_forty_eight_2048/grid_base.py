import enum
import random


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
    BLOCK = enum.auto()
    WALL = enum.auto()
    CONTINUE = enum.auto()
    END = enum.auto()


class Action(enum.Enum):
    MOVE_DOWN = "down"
    MOVE_LEFT = "left"
    MOVE_RIGHT = "right"
    MOVE_UP = "up"
    EXIT = "exit"
    NOTHING = "nothing"


def rgb_bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


def rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def reset() -> str:
    return "\033[0m"


value_color = {
    2: f"{rgb(0, 0, 0)}{rgb_bg(255, 255, 255)}",
    4: f"{rgb(0, 0, 0)}{rgb_bg(150, 150, 255)}",
    8: f"{rgb(0, 0, 0)}{rgb_bg(100, 255, 100)}",
    16: f"{rgb(0, 0, 0)}{rgb_bg(255, 100, 100)}",
    32: f"{rgb(0, 0, 0)}{rgb_bg(150, 150, 150)}",
    64: f"{rgb(0, 0, 0)}{rgb_bg(200, 150, 100)}",
    128: f"{rgb(0, 0, 0)}{rgb_bg(255,182,193)}",
    256: f"{rgb(0, 0, 0)}{rgb_bg(255, 255, 0)}",
    512: f"{rgb(0, 0, 0)}{rgb_bg(100, 250, 250)}",
    1024: f"{rgb(0, 0, 0)}{rgb_bg(255, 0, 255)}",
    2048: f"{rgb(0, 0, 0)}{rgb_bg(255, 99, 71)}",
}


class Cell:
    def __init__(self, state: State = State.BLOCK, value: int = 0) -> None:
        self.state: State = state
        self.value: int = value
        self.down: "Cell"
        self.up: "Cell"
        self.right: "Cell"
        self.left: "Cell"

    def __str__(self) -> str:
        match self:
            case self if self.state == State.WALL:
                return "🔹"
            case self if self.value:
                value = str(self.value).center(6)[2:4]
                return f"{value_color[self.value]}{value}{reset()}"
            case self if self.right.value:
                value = str(self.right.value).center(6)[:2]
                return f"{value_color[self.right.value]}{value}{reset()}"
            case self if self.left.value:
                value = str(self.left.value).center(6)[4:]
                return f"{value_color[self.left.value]}{value}{reset()}"
        margin_value = (
            self.down.value
            or self.up.value
            or (getattr(self.down.left, "value") if hasattr(self.down, "left") else 0)
            or (getattr(self.down.right, "value") if hasattr(self.down, "right") else 0)
            or (getattr(self.up.right, "value") if hasattr(self.up, "right") else 0)
            or int(getattr(self.up.left, "value") if hasattr(self.up, "left") else 0)
        )
        if margin_value:
            return f"{value_color[int(margin_value)]}  {reset()}"
        return f"{rgb_bg(0, 0, 0)}  {reset()}"


class Board:
    def __init__(self, size: int) -> None:
        self.size = size * 3 + 2
        self.player_state: State = State.CONTINUE
        self.cells: list[list[Cell]]
        self.valuable_cells: list[Cell]
        self.set_initial()

    def set_initial(self) -> None:
        self.set_cells()
        self.set_walls()
        self.set_cells_neighboring()
        self.set_valuable_cells()
        self.set_init_value_cell()

    def set_cells(self) -> None:
        self.cells = [[Cell() for _ in range(self.size)] for _ in range(self.size)]

    def set_walls(self) -> None:
        for i in range(self.size):
            for j in [0, self.size - 1]:
                self.cells[i][j].state = State.WALL
                self.cells[j][i].state = State.WALL

    def set_cells_neighboring(self) -> None:
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                self.cells[i][j].left = self.cells[i][j - 1]
                self.cells[i][j].right = self.cells[i][j + 1]
                self.cells[i][j].up = self.cells[i - 1][j]
                self.cells[i][j].down = self.cells[i + 1][j]

    def set_valuable_cells(self) -> None:
        self.valuable_cells = [
            self.cells[i][j]
            for i in range(2, self.size, 3)
            for j in range(2, self.size, 3)
        ]

    def set_init_value_cell(self) -> None:
        self.valuable_cells[0].value = 2
        self.valuable_cells[-3].value = 2

    def take(self, ch: str) -> None:
        for _ in range(int(pow(len(self.valuable_cells), 0.5))):
            match ch:
                case " ":
                    self.player_state = State.END
                case "w":
                    self.move(Action.MOVE_UP.value)
                case "s":
                    self.move(Action.MOVE_DOWN.value)
                case "a":
                    self.move(Action.MOVE_LEFT.value)
                case "d":
                    self.move(Action.MOVE_RIGHT.value)
        new_valuable_cell = list(filter(lambda c: not c.value, self.valuable_cells))
        if new_valuable_cell:
            random.choice(new_valuable_cell).value = 2
        else:
            self.player_state = State.END

    def move(self, direction: str) -> None:
        for c in self.valuable_cells:
            if getattr(getattr(c, direction), direction).state == State.BLOCK:
                d_cell = getattr(getattr(getattr(c, direction), direction), direction)
                if d_cell.value == c.value:
                    d_cell.value += c.value
                    c.value = 0
                elif c.value and not d_cell.value:
                    d_cell.value = c.value
                    c.value = 0
                if d_cell.value == 2048:
                    self.player_state = State.END
                    break

    def __str__(self) -> str:
        return "\n".join(["".join(map(str, rows)) for rows in self.cells])


def run() -> None:
    board = Board(4)
    print(f"\033[H\033[J{board}")
    while board.player_state != State.END:
        board.take(getch())
        print(f"\033[H\033[J{board}")


if __name__ == "__main__":
    run()
