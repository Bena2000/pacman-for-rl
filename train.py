from copy import deepcopy

import numpy as np
from pacman.BenioPacmanFunctionValueApproximation import BenioPacmanFunctionValueApproximation
from pacman.Ghost import Ghosts
from pacman.Pacman import RandomPacman
from pacman.Game import Game

class RandomPacman1(RandomPacman):
    def __init__(self, print_status=True) -> None:
        super().__init__(print_status)

class RandomPacman2(RandomPacman):
    def __init__(self, print_status=True) -> None:
        super().__init__(print_status)

class RandomPacman3(RandomPacman):
    def __init__(self, print_status=True) -> None:
        super().__init__(print_status)

board = ["*   g",
         "gwww ",
         " w*  ",
         " www ",
         "p + p"]

board_big = ["wwwwwwwwwwwwwwwwwwwwwwwwwwww",
             "wp***********ww***********pw",
             "w*wwww*wwwww*ww*wwwww*wwww*w",
             "w+wwww*wwwww*ww*wwwww*wwww+w",
             "w*wwww*wwwww*ww*wwwww*wwww*w",
             "w**************************w",
             "w*wwww*ww*wwwwwwww*ww*wwww*w",
             "w*wwww*ww*wwwwwwww*ww*wwww*w",
             "w*****iww****ww****wwd*****w",
             "wwwwww*wwwww ww wwwww*wwwwww",
             "wwwwww*wwwww ww wwwww*wwwwww",
             "wwwwww*ww          ww*wwwwww",
             "wwwwww*ww www  www ww*wwwwww",
             "wwwwww*ww wwwggwww ww*wwwwww",
             "   z  *   www  www   *  z   ",
             "wwwwww*ww wwwggwww ww*wwwwww",
             "wwwwww*ww wwwwwwww ww*wwwwww",
             "wwwwww*ww s      s ww*wwwwww",
             "wwwwww*ww wwwwwwww ww*wwwwww",
             "wwwwww*ww wwwwwwww ww*wwwwww",
             "w*****i******ww******d*****w",
             "w*wwww*wwwww*ww*wwwww*wwww*w",
             "w*wwww*wwwww*ww*wwwww*wwww*w",
             "w+**ww****************ww**+w",
             "www*ww*ww*wwwwwwww*ww*ww*www",
             "www*ww*ww*wwwwwwww*ww*ww*www",
             "w******ww****ww****ww******w",
             "w*wwwwwwwwww*ww*wwwwwwwwww*w",
             "w*wwwwwwwwww*ww*wwwwwwwwww*w",
             "wp************************pw",
             "wwwwwwwwwwwwwwwwwwwwwwwwwwww"]

GHOSTS = [Ghosts.RED, Ghosts.PINK, Ghosts.BLUE, Ghosts.ORANGE]

def test(n_games=30):
    stats = {}
    pacmans = [
        BenioPacmanFunctionValueApproximation(train=True, use_predefined_weights=False),
        RandomPacman1(print_status=False),
        RandomPacman2(print_status=False),
        RandomPacman3(print_status=False)
    ]
    for pacman in pacmans:
        stats[pacman.__class__.__name__] = []

    for i in range(n_games):
        print(f"Testing #{i + 1}")
        np.random.shuffle(pacmans)
        new_pacmans = deepcopy(pacmans)
        game = Game(board_big, GHOSTS, new_pacmans, display_mode_on=False, delay=0)
        end_game = game.run()
        for pacman, value in end_game.items():
            stats[pacman.__class__.__name__].append(value)
            print(f"{pacman.__class__.__name__}: {value}", end="\t")
        print()

    sorted_stats = dict(sorted(stats.items(), key=lambda x:np.mean(x[1]), reverse=True))
    for i, (pacman_name, values) in enumerate(sorted_stats.items()):
        print(f"{i + 1}.\t{pacman_name}\t{values}\t{np.mean(values)}")

if __name__ == "__main__":
    test()