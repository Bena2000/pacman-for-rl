import random
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict
from .Direction import Direction
from pacman.Pacman import Pacman
from .Position import Position
from .GameState import GameState


def manhattan_distance(point1, point2):
    return abs(point2.x - point1.x) + abs(point2.y - point1.y)

class ReflexAgent:

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
        next_position = self.add_direction_to_position(deepcopy(current_position), move)
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

    def generate_successor_gamestate(self, currentGameState: GameState,  move: Direction):
        game_state = deepcopy(currentGameState)

        player_position = game_state.you['position']
        new_position = self.add_direction_to_position(player_position, move)

        game_state.you['position'] = new_position
        return game_state

    def evaluationFunction(self, currentGameState: GameState, move):

        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = self.generate_successor_gamestate(currentGameState, move)
        newPos = successorGameState.you['position']
        food = successorGameState.big_points.union(successorGameState.double_points).union(successorGameState.points)
        # food = successorGameState.big_points if len(successorGameState.big_points)>0 else successorGameState.double_points if len(successorGameState.double_points)>0 else successorGameState.points
        add_score = 0
        score = 0

        # FOOD
        closest_food = self.closest_element_in_set(food, newPos)
        min_food_distance = manhattan_distance(newPos, closest_food)
        if min_food_distance <= 1:
            if closest_food in successorGameState.big_points:
                add_score +=30
            elif closest_food in successorGameState.double_points:
                add_score +=15
            else:
                add_score +=10

        score += 10 / (min_food_distance if min_food_distance > 0 else 1) - 4.0 * len(food) + add_score

        # GHOSTS
        closest_ghost, min_ghost_distance = self.find_closest_ghost(successorGameState, newPos)
        if min_ghost_distance < 2:
            score -= 50.0

        for ghost in successorGameState.ghosts:
            score -= manhattan_distance(ghost['position'], newPos)

        return score

    def getAction(self, gameState: GameState):
        legalMoves = self.get_possible_actions(gameState, gameState.you['position'])

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        return legalMoves[chosenIndex]


class BenioPacmanReflex(Pacman):
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

    def make_move(self, game_state: GameState, invalid_move=False) -> Direction:
        pacman_position = game_state.you['position']

        minimax = ReflexAgent()
        move = minimax.getAction(game_state)

        # closest_big_point = self.closest_element_in_set(game_state.big_points, pacman_position)
        # closest_double_point = self.closest_element_in_set(game_state.double_points, pacman_position)
        # closest_point = self.closest_element_in_set(game_state.points, pacman_position)
        #
        # move_big = self.search_to_position_BFS(game_state, pacman_position, closest_big_point)
        # move_double = self.search_to_position_BFS(game_state, pacman_position, closest_double_point)
        # move = self.search_to_position_BFS(game_state, pacman_position, closest_point)

        return move
