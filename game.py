import random
import time
from typing import List

# TODO: clashes


class Figure:
    def __init__(self, idx: int, starting_position: int) -> None:
        self.idx = idx
        self.starting_position: int = starting_position
        self.current_position: int = starting_position
        self.is_done: bool = False
        self.is_start: bool = True

    def move(self, number: int) -> None:
        assert not self.is_done, "Cannot move figure thats already done."
        if self.is_start:
            self.is_start = number != 6
        else:
            new_position = (self.current_position + number) % 40
            if (
                self.current_position < self.starting_position
                and self.starting_position <= new_position
            ):
                self.is_done = True
            else:
                self.current_position = new_position

    def is_movable(self):
        return not (self.is_start or self.is_done)


class Player:
    def __init__(self, idx: int) -> None:
        self.idx = idx
        self.figures = [Figure(i, idx * 10) for i in range(4)]

    def has_won(self) -> bool:
        return all(figure.is_done for figure in self.figures)

    def can_move(self) -> bool:
        return not all(figure.is_start | figure.is_done for figure in self.figures)

    def _movable_figures(self) -> List[Figure]:
        return [figure for figure in self.figures if figure.is_movable()]

    # always select the figure that is furthest along
    def _select_figure(self, roll: int) -> Figure:
        for figure in self.figures:
            if (
                figure.is_movable()
                and figure.current_position == figure.starting_position
            ):
                return figure

        if roll == 6:
            for figure in self.figures:
                if figure.is_start:
                    return figure

        if self.can_move():
            movable_figures = self._movable_figures()
            figure_pos = {
                i: figure.current_position + 40
                if figure.current_position < figure.starting_position
                else figure.current_position
                for i, figure in enumerate(movable_figures)
            }
            return movable_figures[max(figure_pos, key=lambda k: figure_pos[k])]
        else:
            return next(figure for figure in self.figures if not figure.is_done)

    def _roll_dice(self) -> int:
        n_throws = 1 if self.can_move() else 3
        return max(random.randint(1, 6) for _ in range(n_throws))

    def move(self) -> int:
        roll = self._roll_dice()
        figure = self._select_figure(roll)
        figure.move(roll)
        return roll

    def play(self) -> None:
        roll = self.move()
        while not self.has_won() and roll == 6:
            roll = self.move()


class Game:
    def __init__(self) -> None:
        self.players = [Player(i) for i in range(1, 4)]
        random.shuffle(self.players)  # someone different should start every time

    def run_game(self, print_board: bool = False) -> Player:
        while True:
            for player in self.players:
                player.play()
                if print_board:
                    print(self)
                    time.sleep(1)
                if player.has_won():
                    return player

    def __repr__(self) -> str:
        board = ["*"] * 40
        start = [["S" for _ in range(4)] for _ in range(3)]
        end = [["E" for _ in range(4)] for _ in range(3)]

        for player in self.players:
            for figure in player.figures:
                if figure.is_start:
                    start[player.idx - 1][figure.idx] = str(player.idx)
                elif figure.is_done:
                    end[player.idx - 1][figure.idx] = str(player.idx)
                else:
                    board[figure.current_position] = str(player.idx)

        cross_board = [
            f"{start[0][0]} {start[0][1]} _ _ {board[18]} {board[19]} {board[20]} _ _ {start[1][0]} {start[1][1]}",
            f"{start[0][2]} {start[0][3]} _ _ {board[17]} {end[1][0]} {board[21]} _ _ {start[1][2]} {start[1][3]}",
            f"_ _ _ _ {board[16]} {end[1][1]} {board[22]} _ _ _ _",
            f"_ _ _ _ {board[15]} {end[1][2]} {board[23]} _ _ _ _",
            f"{board[10]} {board[11]} {board[12]} {board[13]} {board[14]} {end[1][3]} {board[24]} {board[25]} {board[26]} {board[27]} {board[28]}",
            f"{board[9]} {end[0][0]} {end[0][1]} {end[0][2]} {end[0][3]} + {end[2][0]} {end[2][1]} {end[2][2]} {end[2][3]} {board[29]}",
            f"{board[8]} {board[7]} {board[6]} {board[5]} {board[4]} E {board[30]} {board[31]} {board[32]} {board[33]} {board[34]}",
            f"_ _ _ _ {board[3]} E {board[35]} _ _ _ _",
            f"_ _ _ _ {board[2]} E {board[36]} _ _ _ _",
            f"_ _ _ _ {board[1]} E {board[37]} _ _ {start[2][0]} {start[2][1]}",
            f"_ _ _ _ {board[0]} {board[39]} {board[38]} _ _ {start[2][2]} {start[2][3]}",
        ]

        return "\n".join(cross_board) + "\n"


if __name__ == "__main__":
    winner = Game().run_game(print_board=True)
    print(f"{winner.idx} has won.")
