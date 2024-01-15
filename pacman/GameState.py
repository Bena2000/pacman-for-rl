from dataclasses import dataclass
from typing import List, Dict, Any, Set, Tuple
from .Position import Position

"""
All info you might need, I hope.
"""


@dataclass
class GameState:
    you: Dict[str, Any]
    other_pacmans: List[Dict[str, Any]]
    ghosts: List[Dict[str, Any]]
    points: Set[Position]
    big_points: Set[Position]
    phasing_points: Set[Position]
    double_points: Set[Position]
    indestructible_points: Set[Position]
    big_big_points: Set[Position]
    walls: Set[Position]
    board_size: Tuple[int, int]

    def __str__(self) -> str:
        game_state = f"""
    GameState:
        you: {self.you}
        other_pacmans: {self.other_pacmans}
        ghosts: {self.ghosts}
        points: {self.points}
        big_points: {self.big_points}
        phasing_points: {self.phasing_points}
        double_points: {self.double_points}
        indestructible_points: {self.indestructible_points}
        big_big_points: {self.big_big_points}
        board_size: {self.board_size}
            """
        return game_state
