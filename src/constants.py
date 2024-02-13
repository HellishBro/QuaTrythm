from enum import Enum, auto

PERFECT_TIMING = 0.05
GOOD_TIMING = 0.1
BAD_TIMING = 0.2

class Ranks(Enum):
    AP = auto()
    FC = auto()
    V = auto()
    S = auto()
    A = auto()
    B = auto()
    C = auto()
    D = auto()
    F = auto()

RANK_COLORS = {
    Ranks.F: (100, 100, 100, 100),
    Ranks.D: (125, 125, 125, 100),
    Ranks.C: (150, 150, 150, 100),
    Ranks.B: (200, 200, 200, 100),
    Ranks.A: (125, 255, 125, 100),
    Ranks.S: (50, 255, 10, 100),
    Ranks.V: (0, 255, 125, 100),
    Ranks.FC: (0, 255, 255, 100),
    Ranks.AP: (255, 255, 0, 100)
}