import math
import random
import dataclasses
import numpy as np
from typing import Dict
from pathlib import Path

from .Pacman import Pacman
from .Direction import Direction
from .Helpers import can_move_in_direction, direction_to_new_position


class BenioPacmanFunctionValueApproximation(Pacman):

    FILENAME = 'weights.txt'
    # WEIGHTS = np.array([
    #     -3.998075444224211822e-02,
    #     5.767725387831480061e-04,
    #     3.803931876970317177e-02,
    #     3.232015249357537978e-02,
    #     0.000000000000000000e+00,
    #     1.378780716908671079e-02,
    #     8.394530077257136846e-02,
    #     0.000000000000000000e+00
    # ])
    WEIGHTS = np.array(
    [
        -1.104652831222984743e-01,
        1.924716765878314037e-03,
        7.922479606183904788e-02,
        2.136582696509965740e-02,
        - 5.143322709876805426e-02,
        6.943267191134847027e-03,
        1.080349504814373529e-01,
        2.987511579494379552e-03
    ])

    def __init__(self, train=False, use_predefined_weights=True, alpha = 0.001, discount = 0.5, epsilon = 0.25):
        super().__init__()
        self.train = train
        self.alpha = alpha
        self.discount = discount
        self.epsilon = epsilon
        self.use_predefined_weights = use_predefined_weights

        self.__weights = self.WEIGHTS if use_predefined_weights else self.__load_weights()
        self.__game_states_history = []
        self.__actions_history = []

    def make_move(self, game_state, invalid_move=False) -> Direction:
        epsilon = self.epsilon if self.train else 0
        should_random = random.random() < epsilon

        if invalid_move:
            action = random.choice(list(Direction))
        elif should_random:
            action = random.choice(self.__get_legal_actions(game_state))
        else:
            action = self.__get_best_action(game_state)

        self.__game_states_history.append(game_state)
        self.__actions_history.append(action)

        return action

    def give_points(self, points):
        self.__update(reward=points)

    def on_win(self, result: Dict["Pacman", int]):
        self.__on_finish()

    def on_death(self):
        self.__update(reward=-50)
        self.__on_finish()

    def __on_finish(self):
        if self.train:
            self.__save_weights()

    def __load_weights(self):
        path = Path(self.FILENAME)
        if not path.exists():
            return None
        else:
            return np.loadtxt(self.FILENAME)

    def __save_weights(self):
        np.savetxt(self.FILENAME, self.__weights)

    def __update(self, reward):
        prev_state = self.__game_states_history[-2] if len(self.__game_states_history) > 1 else None
        state = self.__game_states_history[-1] if len(self.__game_states_history) > 0 else None
        action = self.__actions_history[-1] if len(self.__actions_history) > 0 else None
        if prev_state is None or state is None or not self.train:
            return

        distances_and_nearest = self.__get_distances_and_nearest(prev_state, action)

        if self.__weights is None:
            self.__weights = np.zeros((len(distances_and_nearest),))

        # błąd tymczasowy
        delta = (reward + self.discount * self.__get_value(state)) - self.__get_qvalue(prev_state, action)
        # aktualizacja wag
        self.__weights += self.alpha * delta * distances_and_nearest

    def __get_best_action(self, game_state) -> Direction:
        legal_actions = self.__get_legal_actions(game_state)
        qvalues = [self.__get_qvalue(game_state, action) for action in legal_actions]
        best_qvalue = max(qvalues)
        best_actions = [action for action, qvalue in zip(legal_actions, qvalues) if qvalue == best_qvalue]
        best_action = random.choice(best_actions)
        return best_action

    def __get_legal_actions(self, game_state) -> list[Direction]:
        directions = []
        for direction in Direction:
            position = game_state.you['position']
            phasing = game_state.you['is_phasing']

            if can_move_in_direction(position, direction, game_state.walls, game_state.board_size, phasing):
                directions.append(direction)

        return directions

    def __get_value(self, game_state) -> float:
        possible_actions = self.__get_legal_actions(game_state)

        if len(possible_actions) == 0:
            return 0.0

        return max([self.__get_qvalue(game_state, action) for action in possible_actions])

    def __get_qvalue(self, game_state, action) -> float:
        distances_and_nearest = self.__get_distances_and_nearest(game_state, action)
        if self.__weights is None:
            self.__weights = np.random.random((len(distances_and_nearest),))

        qvalue = 0
        for i in range(len(distances_and_nearest)):
            qvalue += self.__weights[i] * distances_and_nearest[i]
        return qvalue

    # Wartości z mapy
    def __get_distances_and_nearest(self, game_state, action):
        next_game_state = self.__get_state_after_action(game_state, action)
        nearest_ghost_distance = self.__get_nearest_ghost_distance(next_game_state)
        nearest_player_distance = self.__get_nearest_player_distance(next_game_state)
        double_point_distance = self.__get_double_point_distance(next_game_state)
        big_points_distance = self.__get_big_points_distance(next_game_state)
        big_big_point_distance = self.__get_big_big_points_distance(next_game_state)
        indestructible_distance = self.__get_indestructible_distance(next_game_state)
        point_distance = self.__get_point_distance(next_game_state)
        nearest_eatable = self.__get_nearest_eatable(next_game_state)

        return np.array([
            nearest_ghost_distance,
            nearest_player_distance,
            double_point_distance,
            big_points_distance,
            big_big_point_distance,
            indestructible_distance,
            point_distance,
            nearest_eatable,
        ])

    def __get_nearest_eatable(self, game_state):
        eatable_ghosts = [ghost_info['position'] for ghost_info in game_state.ghosts if ghost_info['is_eatable']]
        eatable_players = [player_info['position'] for player_info in game_state.other_pacmans if player_info['is_eatable']]
        eatable_positions = eatable_ghosts + eatable_players

        if len(eatable_positions) == 0:
            return 0

        distance = self.__get_distance_to_nearest(game_state.you['position'], eatable_positions)

        distance = min(10, distance) / 10
        rev_distance = 1 - distance
        return rev_distance

    def __get_nearest_ghost_distance(self, game_state):
        is_indestructible = self.__is_timer_enabled(game_state.you['is_indestructible'])
        if is_indestructible:
            return 0

        ghost_positions = [ghost_info['position'] for ghost_info in game_state.ghosts if not ghost_info['is_eatable']]
        if len(ghost_positions) == 0:
            return 0

        distance = self.__get_distance_to_nearest(game_state.you['position'], ghost_positions)

        distance = min(5, distance) / 5
        rev_distance = 1 - distance
        return rev_distance

    def __get_nearest_player_distance(self, game_state):
        is_indestructible = self.__is_timer_enabled(game_state.you['is_indestructible'])
        if is_indestructible:
            return 0

        players_positions = [pacman_info['position'] for pacman_info in game_state.other_pacmans if not pacman_info['is_eatable']]
        if len(players_positions) == 0:
            return 0

        distance = self.__get_distance_to_nearest(game_state.you['position'], players_positions)

        distance = min(5, distance) / 5
        rev_distance = 1 - distance
        return rev_distance

    def __get_double_point_distance(self, game_state):
        is_active = self.__is_timer_enabled(game_state.you['double_points_timer'])
        if is_active:
            return 1.0

        distance = self.__get_distance_to_nearest(game_state.you['position'], game_state.double_points)
        if distance is None:
            return 0

        distance = min(15, distance) / 15
        rev_distance = 1 - distance
        return rev_distance

    def __get_indestructible_distance(self, game_state):
        is_active = self.__is_timer_enabled(game_state.you['is_indestructible'])
        if is_active:
            return 1.0

        distance = self.__get_distance_to_nearest(game_state.you['position'], game_state.indestructible_points)
        if distance is None:
            return 0

        distance = min(15, distance) / 15
        rev_distance = 1 - distance
        return rev_distance

    def __get_big_points_distance(self, game_state):
        distance = self.__get_distance_to_nearest(game_state.you['position'], game_state.big_points)
        if distance is None:
            return 0

        distance = min(15, distance) / 15
        rev_distance = 1 - distance
        return rev_distance

    def __get_big_big_points_distance(self, game_state):
        distance = self.__get_distance_to_nearest(game_state.you['position'], game_state.big_big_points)
        if distance is None:
            return 0

        distance = min(15, distance) / 15
        rev_distance = 1 - distance
        return rev_distance

    def __get_point_distance(self, game_state):
        distance = self.__get_distance_to_nearest(game_state.you['position'], game_state.points)
        if distance is None:
            return 0

        distance = min(4, distance) / 4
        rev_distance = 1 - distance
        return rev_distance

    def __get_state_after_action(self, game_state, action):
        next_state = self.__copy_game_state(game_state)
        next_state.you['position'] = direction_to_new_position(next_state.you['position'], action, game_state.board_size)
        return next_state

    # pomocne
    def __copy_game_state(self, game_state):
        new_you = dict(game_state.you)
        new_game_state = dataclasses.replace(game_state, you=new_you)
        return new_game_state

    def __get_distance_to_nearest(self, start_point, end_points) -> int | None:
        if len(end_points) == 0:
            return None
        distances = []
        for end_point in end_points:
            distance = self.__get_manhattan_distance(start_point, end_point)
            distances.append(distance)
        return min(distances)

    def __get_manhattan_distance(self, start, end):
        return abs(end.x - start.x) + abs(end.y - start.y)

    def __get_euclidean_distance(self, start, end):
        return math.sqrt((end.x - start.x) ** 2 + (end.y - start.y) ** 2)

    def __is_timer_enabled(self, timer, min_bound=4):
        return timer is not None and timer > min_bound