import random
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict
from .Direction import Direction
from pacman.Pacman import Pacman
from .Position import Position
from .GameState import GameState

class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
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
        ghosts_positions = [ghost['position'] for ghost in game_state.ghosts]

        if next_position in game_state.walls or next_position in ghosts_positions:
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


    def closest_point(self, points: set[Position], pacman_position: Position)->Position|None:
        if len(points)<=0:
            return None

        closest_point: Position =list(points)[0]
        closest_point_distance = manhattan_distance(closest_point, pacman_position)

        for point in points:
            distance = manhattan_distance(point, pacman_position)
            if distance < closest_point_distance:
                closest_point = point
                closest_point_distance = distance
        return closest_point

    def search_to_position_BFS(self, game_state: GameState, start_position: Position, end_position: Position):
        queue = Queue()
        visitedNodes = []
        queue.push((start_position, []))

        while not queue.isEmpty():
            current_position, steps = queue.pop()
            if current_position not in visitedNodes:
                visitedNodes.append(current_position)

                if current_position == end_position:
                    return steps[0]

                for move_direction in self.get_possible_actions(game_state, current_position):
                    next_position = self.add_direction_to_position(current_position, move_direction)
                    queue.push((next_position, steps + [move_direction]))
        return random.choice(list(Direction))

    def make_move(self, game_state: GameState, invalid_move=False) -> Direction:
        pacman_position = game_state.you['position']
        closest_point = self.closest_point(game_state.points, pacman_position)
        move = self.search_to_position_BFS(game_state, pacman_position, closest_point)
        return move


