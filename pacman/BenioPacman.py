import random
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict
from .Direction import Direction
from pacman.Pacman import Pacman
from .Position import Position

def manhattan_distance(point1, point2):
    return abs(point2.x - point1.x) + abs(point2.y - point1.y)

class BenioPacman(Pacman):
    def __init__(self, print_status=True) -> None:
        self.print_status = print_status
    def give_points(self, points):
        if self.print_status:
            print(f"Benio pacman got {points} points")

    def on_death(self):
        if self.print_status:
            print("Benio pacman dead")

    def on_win(self, result: Dict["Pacman", int]):
        if self.print_status:
            print("Benio pacman won")

    def validate_move(self, game_state, move: Direction) -> bool:
        next_position: Position = deepcopy(game_state.you['position'])

        if move == Direction.UP:
            next_position.y += 1
        elif move == Direction.DOWN:
            next_position.y -= 1
        elif move == Direction.LEFT:
            next_position.x -= 1
        else:
            next_position.x += 1

        if next_position in game_state.walls:
            return False
        return True

    def closest_point(self, points, pacman_position):
        closest_point: Position =list(points)[0]
        closest_point_distance = manhattan_distance(closest_point, pacman_position)
        for point in points:
            distance = manhattan_distance(point, pacman_position)
            if distance < closest_point_distance:
                closest_point = point
                closest_point_distance = distance
        return closest_point

    def make_move(self, game_state, invalid_move=False) -> Direction:
        pacman_position = game_state.you['position']

        closest_point = self.closest_point(game_state.points, pacman_position)
        # validate_move(game_state, Direction.RIGHT)
        return random.choice(list(Direction))  # it will make some valid move at some point
