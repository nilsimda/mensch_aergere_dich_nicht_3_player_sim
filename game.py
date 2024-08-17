import random
from typing import List

# TODO: clashes


class Figure:
    def __init__(self, starting_position: int) -> None:
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


class Player:
    def __init__(self, idx: int, color: str) -> None:
        self.idx = idx
        self.color = color
        self.figures = [Figure(idx * 10) for _ in range(4)]

    def has_won(self) -> bool:
        return all(figure.is_done for figure in self.figures)

    def can_move(self) -> bool:
        return not all(figure.is_start | figure.is_done for figure in self.figures)

    def _movable_figures(self) -> List[Figure]:
        return [
            figure for figure in self.figures if not (figure.is_done or figure.is_start)
        ]

    # always select the figure that is furthest along
    # TODO: move from start square
    # TODO: move figure from start if its a six
    def _select_figure(self) -> Figure:
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
            return [figure for figure in self.figures if not figure.is_done][0]

    def _roll_dice(self) -> int:
        n_throws = 1 if self.can_move() else 3
        return max(random.randint(1, 6) for _ in range(n_throws))

    def move(self) -> None:
        figure = self._select_figure()
        roll = self._roll_dice()
        figure.move(roll)
        while not figure.is_done and roll == 6:
            roll = self._roll_dice()
            figure.move(roll)


class Game:
    def __init__(self) -> None:
        self.colors = ["🟡", "🔵", "🟢"]
        self.players = [Player(i, color) for i, color in zip(range(1, 4), self.colors)]
        random.shuffle(self.players)  # someone different should start every time

    def run_game(self, print_board: bool = False) -> Player:
        while True:
            for player in self.players:
                player.move()
                if print_board:
                    print(self)
                if player.has_won():
                    return player

    # TODO: Cross shaped repr
    def __repr__(self) -> str:
        board = ["."] * 40

        for player in self.players:
            for figure in player.figures:
                if not (figure.is_start or figure.is_done):
                    board[figure.current_position] = player.color

        return " ".join(board)


if __name__ == "__main__":
    winner = Game().run_game(print_board=True)
    print(f"{winner.color} has won.")
