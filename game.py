import random
import time
from termcolor import colored
import argparse


# TODO: allow variable number of players, argparse
# TODO: force players to kick figure if possible
# TODO: different policies (random, move first, move last, no overtaking)
# TODO: testing


class Figure:
    def __init__(self, idx: int, starting_position: int) -> None:
        self.idx = idx
        self.starting_position: int = starting_position
        self.current_position: int = starting_position
        self.is_done: bool = False
        self.is_start: bool = True

    def move(self, number: int, other_players: list) -> None:
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
                for other_player in other_players:
                    for other in other_player.figures:
                        if (
                            other.is_movable()
                            and other.current_position == self.current_position
                        ):
                            other.is_start = True
                            other.current_position = other.starting_position

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

    def _movable_figures(self) -> list[Figure]:
        return [figure for figure in self.figures if figure.is_movable()]

    # always select the figure that is furthest along
    def _select_figure(self, roll: int) -> Figure:
        for figure in self.figures:  # clear starting position
            if (
                figure.is_movable()
                and figure.current_position == figure.starting_position
            ):
                return figure

        if roll == 6:  # move new figure to start if possible
            for figure in self.figures:
                if figure.is_start:
                    return figure

        if self.can_move():  # actual move policy
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

    def move(self, other_players: list) -> int:
        roll = self._roll_dice()
        figure = self._select_figure(roll)
        figure.move(roll, other_players)
        return roll

    def play(self, other_players: list) -> None:
        roll = self.move(other_players)
        while not self.has_won() and roll == 6:
            roll = self.move(other_players)


class Game:
    def __init__(self) -> None:
        self.players = [Player(i) for i in range(1, 4)]
        random.shuffle(self.players)  # someone different should start every time

    def run_game(self, print_board: bool = False, sleep_time: float = 1) -> Player:
        while True:
            for player in self.players:
                other_players = [
                    other_player
                    for other_player in self.players
                    if other_player != player
                ]
                player.play(other_players)
                if print_board:
                    print(self)
                    time.sleep(sleep_time)
                if player.has_won():
                    return player

    def __repr__(self) -> str:
        colors: list = ["yellow", "green", "red", "blue"]
        board = ["*" for _ in range(40)]
        start = [[colored("S", colors[i]) for _ in range(4)] for i in range(3)]
        end = [[colored("E", colors[i]) for _ in range(4)] for i in range(3)]

        for player in self.players:
            for figure in player.figures:
                if figure.is_start:
                    start[player.idx - 1][figure.idx] = colored(
                        str(player.idx), colors[player.idx - 1]
                    )
                elif figure.is_done:
                    end[player.idx - 1][figure.idx] = colored(
                        str(player.idx), colors[player.idx - 1]
                    )
                else:
                    board[figure.current_position] = colored(
                        str(player.idx), colors[player.idx - 1]
                    )

        cross_board = [
            f"{start[0][0]} {start[0][1]} _ _ {board[18]} {board[19]} {board[20]} _ _ {start[1][0]} {start[1][1]}",
            f"{start[0][2]} {start[0][3]} _ _ {board[17]} {end[1][0]} {board[21]} _ _ {start[1][2]} {start[1][3]}",
            f"_ _ _ _ {board[16]} {end[1][1]} {board[22]} _ _ _ _",
            f"_ _ _ _ {board[15]} {end[1][2]} {board[23]} _ _ _ _",
            f"{board[10]} {board[11]} {board[12]} {board[13]} {board[14]} {end[1][3]} {board[24]} {board[25]} {board[26]} {board[27]} {board[28]}",
            f"{board[9]} {end[0][0]} {end[0][1]} {end[0][2]} {end[0][3]} + {end[2][0]} {end[2][1]} {end[2][2]} {end[2][3]} {board[29]}",
            f"{board[8]} {board[7]} {board[6]} {board[5]} {board[4]} E {board[34]} {board[33]} {board[32]} {board[31]} {board[30]}",
            f"_ _ _ _ {board[3]} E {board[35]} _ _ _ _",
            f"_ _ _ _ {board[2]} E {board[36]} _ _ _ _",
            f"_ _ _ _ {board[1]} E {board[37]} _ _ {start[2][0]} {start[2][1]}",
            f"_ _ _ _ {board[0]} {board[39]} {board[38]} _ _ {start[2][2]} {start[2][3]}",
        ]

        return "\n".join(cross_board) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s",
        "--sleep_time",
        type=float,
        help="the amount of time to sleep between printing each new board state",
        default=0,
    )

    parser.add_argument(
        "-p",
        "--print_board",
        action="store_true",
        help="wether to print the board for each step or just show the winner",
    )

    parser.add_argument(
        "-n",
        "--number_of_players",
        type=int,
        help="The number of players (has to be between 2 and 4, both included)",
        default=3,
    )

    args = parser.parse_args()

    if args.number_of_players > 4 or args.number_of_players < 2:
        raise Exception(
            f"Number of Players has to be between 2 and 4, but was {args.number_of_players}"
        )

    winner = Game().run_game(print_board=args.print_board, sleep_time=args.sleep_time)
    print(f"{winner.idx} has won.")
