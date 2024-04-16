from enum import Enum, auto


class AlgorithmType(Enum):
    ESTIMATION = auto()
    LOADFLOW = auto()
    NONE = auto()
    INVALID = auto()


class AlgorithmAim(Enum):
    MAIN_SIMULATION = auto()
    VALIDATION = auto()
    INVALID = auto()
