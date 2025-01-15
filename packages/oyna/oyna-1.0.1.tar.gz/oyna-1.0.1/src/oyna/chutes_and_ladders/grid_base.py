import enum
import random
from itertools import permutations
from time import sleep


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
    DESTINATION = "🍭"
    WALL = "🔹"
    UP = "⏫"
    DOWN = "⏬"
    LEFT = "⏪"
    RIGHT = "⏩"
    PLAYER = "😸"
    ENEMY = "🐶"
    END = "  "


class Direction(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    DOWN = "down"
    UP = "up"


class Cell:
    def __init__(self, state: State = State.BLOCK) -> None:
        self.player_is_here: bool = False
        self.enemy_is_here: bool = False
        self.direction: Direction = Direction.LEFT
        self.state = state
        self.down: "Cell"
        self.up: "Cell"
        self.right: "Cell"
        self.left: "Cell"

    def __str__(self) -> str:
        if self.player_is_here:
            return str(State.PLAYER.value)
        if self.enemy_is_here:
            return str(State.ENEMY.value)
        return str(self.state.value)

    def set_neighbors(
        self, left: "Cell", right: "Cell", up: "Cell", down: "Cell"
    ) -> None:
        self.down = down
        self.up = up
        self.right = right
        self.left = left


class Board:
    def __init__(self, size: int) -> None:
        self.player: Cell
        self.enemy: Cell
        self.dice: int = 0
        self.enemy_dice: int = 0
        self.size = size + 2
        self.cells = self._cells()
        self.set_initial()

    def _cells(self) -> list[list[Cell]]:
        return [[Cell() for _ in range(self.size)] for _ in range(self.size)]

    def set_initial(self) -> None:
        self.set_walls()
        self.set_directions()
        self.set_cells_neighboring()
        self.set_players()
        self.set_ladders()
        self.set_destination()

    def set_destination(self) -> None:
        self.cells[1][1].state = State.DESTINATION

    def set_directions(self) -> None:
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                self.cells[i][j].direction = (
                    Direction.RIGHT if i % 2 == 0 else Direction.LEFT
                )
            j_ = self.size - 2 if i % 2 == 0 else 1
            self.cells[i][j_].direction = Direction.UP

    def set_ladders(self) -> None:
        ladders = random.sample(
            list(permutations(range(1, self.size - 1), 2)),
            (self.size // 2) ** 2,
        )

        for ladder in ladders:
            cell = self.cells[ladder[0]][ladder[1]]

            if cell.state == State.BLOCK and not cell.player_is_here:
                match random.choice(
                    [d.value for d in Direction] + [Direction.DOWN.value]
                ):
                    case Direction.LEFT.value:
                        if cell.left.state not in [State.RIGHT, State.WALL]:
                            cell.state = State.LEFT
                    case Direction.RIGHT.value:
                        if cell.right.state not in [State.LEFT, State.WALL]:
                            cell.state = State.RIGHT
                    case Direction.UP.value:
                        if cell.up.state not in [State.DOWN, State.WALL]:
                            cell.state = State.UP
                    case Direction.DOWN.value:
                        if cell.down.state not in [State.UP, State.WALL]:
                            cell.state = State.DOWN

    def set_walls(self) -> None:
        for i in range(self.size):
            for j in [0, self.size - 1]:
                self.cells[j][i].state = State.WALL
                self.cells[i][j].state = State.WALL

    def set_cells_neighboring(self) -> None:
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                self.cells[i][j].set_neighbors(
                    self.cells[i][j - 1],
                    self.cells[i][j + 1],
                    self.cells[i - 1][j],
                    self.cells[i + 1][j],
                )

    def set_players(self) -> None:
        self.player = self.cells[self.size - 2][1]
        self.enemy = self.cells[self.size - 2][1]
        self.player.player_is_here = True
        self.enemy.enemy_is_here = True

    def action(self, ch: str) -> None:
        match ch:
            case " ":
                self.player.state = State.END
            case _:
                self.dice = random.randint(1, 6)
                self.enemy_dice = random.randint(1, 6)

                if self.check_allowed_move(self.player, self.dice):
                    for _ in range(self.dice):
                        move = getattr(self.player, self.player.direction.value)
                        self.player.player_is_here = False
                        self.player = move
                        self.player.player_is_here = True
                        sleep(0.3)
                        print(self)
                    self.player = self.move_on_ladder(self.player)

                if self.check_allowed_move(self.enemy, self.enemy_dice):
                    for _ in range(self.enemy_dice):
                        move = getattr(self.enemy, self.enemy.direction.value)
                        self.enemy.enemy_is_here = False
                        self.enemy = move
                        self.enemy.enemy_is_here = True
                        sleep(0.3)
                        print(self)
                    self.enemy = self.move_on_ladder(self.enemy)
                if (
                    self.player.state == State.DESTINATION
                    or self.enemy.state == State.DESTINATION
                ):
                    self.player.state = State.END

    def move_on_ladder(self, cell: Cell) -> Cell:
        if cell.state.name in [d.name for d in Direction]:
            new_position = getattr(cell, cell.state.name.lower())
            new_position.player_is_here = cell.player_is_here
            new_position.enemy_is_here = cell.enemy_is_here
            cell.player_is_here = cell.enemy_is_here = False
            sleep(0.3)
            print(self)
            return self.move_on_ladder(new_position)
        else:
            return cell

    def check_allowed_move(self, cell: Cell, dice: int) -> bool:
        for _ in range(self.dice - 1):
            if cell.direction:
                move = getattr(cell, cell.direction.value)
                if move.state == State.DESTINATION:
                    return False
                cell = move
            else:
                return False
        return True

    def __str__(self) -> str:
        return (
            "\033[H\033[J"
            + "\n".join(["".join([str(cell) for cell in rows]) for rows in self.cells])
            + f"\n You 😸: {self.dice} Enemy  🐶: {self.enemy_dice} "
        )


class Game:
    def __init__(self) -> None:
        self.board = Board(10)

    def run(self) -> None:
        print(self.board)
        while self.board.player.state != State.END:
            self.board.action(getch())
        self.print_result()

    def print_result(self) -> None:
        self.board.player.player_is_here = False


def run() -> None:
    Game().run()


if __name__ == "__main__":
    run()
