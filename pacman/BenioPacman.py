import random
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict
from .Direction import Direction
from pacman.Pacman import Pacman
from .Position import Position
from .GameState import GameState

class Queue:
    def __init__(self):
        self.list = []

    def push(self,item):
        self.list.insert(0,item)

    def pop(self):
        return self.list.pop()

    def isEmpty(self):
        return len(self.list) == 0

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

    def find_closest_ghost(self, game_state: GameState, position: Position):
        ghosts_positions = [ghost['position'] for ghost in game_state.ghosts]
        closest_ghost = game_state.ghosts[0]
        min_distance = manhattan_distance(position, ghosts_positions[0])
        for idx, ghosts_position in enumerate(ghosts_positions):
            distance = manhattan_distance(position, ghosts_position)
            if distance < min_distance:
                min_distance = distance
                closest_ghost = game_state.ghosts[idx]
        return closest_ghost, min_distance


    def check_if_ghost_in_position(self, game_state, position: Position):
        ghosts_positions = [ghost['position'] for ghost in game_state.ghosts]

        if position in ghosts_positions:
            return True
        return False

    def check_if_ghost_radius_in_position(self, game_state, position: Position, radius = 3):
        ghosts_positions = [ghost['position'] for ghost in game_state.ghosts]

        for ghosts_position in ghosts_positions:
            if manhattan_distance(position, ghosts_position) < radius:
                return True
        return False

    def add_direction_to_position(self, position: Position, direction: Direction)->Position:
        temp_position = deepcopy(position)
        if direction == Direction.UP:
            temp_position.y -= 1
        elif direction == Direction.DOWN:
            temp_position.y += 1
        elif direction == Direction.LEFT:
            temp_position.x -= 1
        elif direction == Direction.RIGHT:
            temp_position.x += 1
        return temp_position

    def validate_move(self, game_state: GameState, current_position: Position, move: Direction) -> bool:
        # next_position: Position = deepcopy(game_state.you['position'])

        next_position = self.add_direction_to_position(deepcopy(current_position), move)
        # ghosts_positions = [ghost['position'] for ghost in game_state.ghosts]

        if next_position in game_state.walls:
            return False
        return True

    def get_possible_actions(self, game_state: GameState, position)->list[Direction]:
        list = []
        if self.validate_move(game_state,position, Direction.UP):
            list.append(Direction.UP)
        if self.validate_move(game_state,position, Direction.DOWN):
            list.append(Direction.DOWN)
        if self.validate_move(game_state,position, Direction.LEFT):
            list.append(Direction.LEFT)
        if self.validate_move(game_state,position, Direction.RIGHT):
            list.append(Direction.RIGHT)
        return list


    def closest_element_in_set(self, elements_set: set[Position], pacman_position: Position)-> Position | None:
        if len(elements_set)<=0:
            return None

        closest_point: Position =list(elements_set)[0]
        closest_point_distance = manhattan_distance(closest_point, pacman_position)

        for point in elements_set:
            distance = manhattan_distance(point, pacman_position)
            if distance < closest_point_distance:
                closest_point = point
                closest_point_distance = distance
        return closest_point

    def search_to_position_BFS(self, game_state: GameState, start_position: Position, end_position: Position):
        if end_position is None or self.check_if_ghost_in_position(game_state, end_position):
            return None

        queue = Queue()
        visitedNodes = []
        queue.push((start_position, []))

        while not queue.isEmpty():
            current_position, steps = queue.pop()
            # if len(steps) < 3 and self.check_if_ghost_radius_in_position(game_state, current_position):
            #     continue
            if current_position not in visitedNodes:
                visitedNodes.append(current_position)

                if current_position == end_position:
                    return steps[0]

                for move_direction in self.get_possible_actions(game_state, current_position):
                    next_position = self.add_direction_to_position(current_position, move_direction)
                    queue.push((next_position, steps + [move_direction]))
        return None

    def make_move(self, game_state: GameState, invalid_move=False) -> Direction:
        pacman_position = game_state.you['position']

        closest_big_point = self.closest_element_in_set(game_state.big_points, pacman_position)
        closest_double_point = self.closest_element_in_set(game_state.double_points, pacman_position)
        closest_point = self.closest_element_in_set(game_state.points, pacman_position)

        move_big = self.search_to_position_BFS(game_state, pacman_position, closest_big_point)
        move_double = self.search_to_position_BFS(game_state, pacman_position, closest_double_point)
        move = self.search_to_position_BFS(game_state, pacman_position, closest_point)

        return move if move is not None else random.choice(list(Direction))
