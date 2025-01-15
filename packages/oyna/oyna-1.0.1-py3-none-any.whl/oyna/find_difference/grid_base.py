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


selected_emoji = random.choice(
    [
        ("😀", "😄"),
        ("😄", "😁"),
        ("😙", "😗"),
        ("🙂", "🙃"),
        ("😏", "😒"),
        ("🤪", "😜"),
        ("🤩", "😍"),
        ("😳", "🙄"),
    ]
)


class State(enum.Enum):
    BLOCK = selected_emoji[0]
    ANSWER = selected_emoji[1]
    INCORRECT_ANSWER = "🟥"
    PLAYER = "🟦"
    WALL = "🔹"
    WIN = "🏆"
    EXIT = "🟦"


class Board:
    def __init__(self, size: int) -> None:
        self.size = size + 2
        self.player: tuple[int, int] = (self.size // 2, self.size // 2)
        self.cells = self._cells()
        self.set_walls()
        self.set_answer()

    def _cells(self) -> list[list[State]]:
        return [[State.BLOCK for _ in range(self.size)] for _ in range(self.size)]

    def set_walls(self) -> None:
        for i in range(self.size):
            for j in [0, self.size - 1]:
                self.cells[j][i] = State.WALL
                self.cells[i][j] = State.WALL

    def set_answer(self) -> None:
        i = random.randint(1, self.size - 2)
        j = random.randint(1, self.size - 2)
        self.cells[i][j] = State.ANSWER

    def action(self, ch: str) -> None:
        match ch:
            case "w":
                self._move_tile(-1, 0)
            case "a":
                self._move_tile(0, -1)
            case "s":
                self._move_tile(1, 0)
            case "d":
                self._move_tile(0, 1)
            case "e":
                self.cells[self.player[0]][self.player[1]] = (
                    State.WIN
                    if self.player_state == State.ANSWER
                    else State.INCORRECT_ANSWER
                )
            case " ":
                self.cells[self.player[0]][self.player[1]] = State.EXIT
            case _:
                pass

    def _move_tile(self, x: int = 0, y: int = 0) -> None:
        self.player = (
            (self.player[0] + x, self.player[1] + y)
            if self.cells[self.player[0] + x][self.player[1] + y] != State.WALL
            else self.player
        )

    @property
    def player_state(self) -> State:
        return self.cells[self.player[0]][self.player[1]]

    def __str__(self) -> str:
        return "\n".join(
            [
                "".join(
                    [
                        f"\033[48;2;50;50;250m{self.cells[row][col].value}\033[0m"
                        if self.player == (row, col)
                        else str(self.cells[row][col].value)
                        for col in range(self.size)
                    ]
                )
                for row in range(self.size)
            ]
        )


def run() -> None:
    board = Board(10)
    print(f"\033[H\033[J{board}")
    while board.player_state not in [State.EXIT, State.WIN]:
        board.action(getch())
        print(f"\033[H\033[J{board}")


if __name__ == "__main__":
    run()
