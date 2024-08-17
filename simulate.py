from game import Game

if __name__ == "__main__":
    rounds = 10_000
    wins_per_player = {1: 0, 2: 0, 3: 0}
    for _ in range(rounds):
        winner = Game().run_game()
        wins_per_player[winner.idx] += 1

    for idx, wins in wins_per_player.items():
        print(f"Player {idx}: {wins} ({wins/rounds * 100 :.2f}%)")
