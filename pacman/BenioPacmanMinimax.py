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

class MinimaxAgent:

    def __init__(self, game_state: GameState, depth: int) -> None:
        self.num_agents = len(game_state.ghosts) + 1
        self.depth = depth

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

    def get_agent_by_index(self,currentGameState: GameState, agent_index: int):
        if agent_index == 0:
            return currentGameState.you
        else:
            return currentGameState.ghosts[agent_index-1]
    def generate_successor_gamestate(self, currentGameState: GameState, agent_index: int, move: Direction):
        game_state = deepcopy(currentGameState)

        agent = self.get_agent_by_index(game_state, agent_index)
        agent_position = agent['position']
        new_position = self.add_direction_to_position(agent_position, move)

        agent['position'] = new_position
        return game_state

    def is_winner(self, currentGameState: GameState):
        if (not currentGameState.points and not currentGameState.big_points) or len(currentGameState.other_pacmans)<=0:
            return True
        return False

    def is_loser(self, currentGameState: GameState):
        ghosts_positions = [ghost['position'] for ghost in currentGameState.ghosts]
        player_position = currentGameState.you['position']
        if player_position in ghosts_positions:
            return True
        return False

    def getAction(self, gameState: GameState):
        # player = ('player', gameState.you['position'])
        return self.maxval(gameState, 0, 0)[0]

    def evaluationFunction(self, currentGameState: GameState):

        # Useful information you can extract from a GameState (pacman.py)

        # player = ('player', currentGameState.you['position'])
        # successorGameState = self.generate_successor_gamestate(currentGameState, player, move)
        newPos = currentGameState.you['position']
        food = currentGameState.big_points if len(currentGameState.big_points)>0 else currentGameState.double_points if len(currentGameState.double_points)>0 else currentGameState.points
        add_score = 0
        score = 0

        # FOOD
        closest_food = self.closest_element_in_set(food, newPos)
        min_food_distance = manhattan_distance(newPos, closest_food)
        if min_food_distance <= 1:
            add_score +=10
        score += 10 / (min_food_distance if min_food_distance > 0 else 1) - 4.0 * len(food) + add_score

        # GHOSTS
        closest_ghost, min_ghost_distance = self.find_closest_ghost(currentGameState, newPos)
        if min_ghost_distance < 2:
            score -= 50.0

        return score

    def minimax(self, gameState: GameState, agent_index, depth):
        if depth is self.depth * self.num_agents or self.is_winner(gameState) or self.is_loser(gameState):
            return self.evaluationFunction(gameState)

        isPlayer: bool = agent_index == 0

        if isPlayer:
            return self.maxval(gameState, agent_index, depth)[1]
        else:
            return self.minval(gameState, agent_index, depth)[1]

    def maxval(self, gameState: GameState, agent_index, depth):
        result = ("max", -float("inf"))
        agent = self.get_agent_by_index(gameState, agent_index)
        for action in self.get_possible_actions(gameState, agent['position']):
            nextStep = self.generate_successor_gamestate(gameState, agent_index, action)
            index = (depth + 1) % self.num_agents

            tempAction = (action, self.minimax(nextStep, index, depth + 1))
            result = tempAction if tempAction[1] > result[1] else result
        return result

    def minval(self, gameState: GameState, agent_index, depth):
        result = ("min", float("inf"))
        agent = self.get_agent_by_index(gameState, agent_index)
        for action in self.get_possible_actions(gameState, agent['position']):
            nextStep = self.generate_successor_gamestate(gameState, agent_index, action)
            index = (depth + 1) % self.num_agents

            tempAction = (action, self.minimax(nextStep, index, depth + 1))
            result = tempAction if tempAction[1] < result[1] else result
        return result

class BenioPacmanMinimax(Pacman):
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

        minimax = MinimaxAgent(game_state, 2)
        move = minimax.getAction(game_state)

        # closest_big_point = self.closest_element_in_set(game_state.big_points, pacman_position)
        # closest_double_point = self.closest_element_in_set(game_state.double_points, pacman_position)
        # closest_point = self.closest_element_in_set(game_state.points, pacman_position)
        #
        # move_big = self.search_to_position_BFS(game_state, pacman_position, closest_big_point)
        # move_double = self.search_to_position_BFS(game_state, pacman_position, closest_double_point)
        # move = self.search_to_position_BFS(game_state, pacman_position, closest_point)

        return move
