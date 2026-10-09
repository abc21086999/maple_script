from enum import Enum, auto

class StateEnum(Enum):
    STATIONARY = auto()
    WALKER = auto()
    WANDER = auto()
    RUNESOLVER = auto()
    PAUSE = auto()
    WALKERCOOLDOWN = auto()
    WANDERCOOLDOWN = auto()
    WAITING = auto()
    WALKERWAITING = auto()
    WANDERWAITING = auto()