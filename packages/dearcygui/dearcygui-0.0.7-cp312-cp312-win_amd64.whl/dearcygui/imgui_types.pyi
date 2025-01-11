"""
This type stub file was generated by cyright.
"""

from enum import IntEnum

def color_as_int(val) -> int:
    """
    Convert any color representation to an integer (packed rgba).
    """
    ...

def color_as_ints(val) -> tuple[int, int, int, int]:
    """
    Convert any color representation to a tuple of integers (r, g, b, a).
    """
    ...

def color_as_floats(val) -> tuple[float, float, float, float]:
    """
    Convert any color representation to a tuple of floats (r, g, b, a).
    """
    ...

class ButtonDirection(IntEnum):
    NONE = ...
    LEFT = ...
    RIGHT = ...
    UP = ...
    DOWN = ...


class AxisScale(IntEnum):
    LINEAR = ...
    TIME = ...
    LOG10 = ...
    SYMLOG = ...


class Axis(IntEnum):
    X1 = ...
    X2 = ...
    X3 = ...
    Y1 = ...
    Y2 = ...
    Y3 = ...


class LegendLocation(IntEnum):
    CENTER = ...
    NORTH = ...
    SOUTH = ...
    WEST = ...
    EAST = ...
    NORTHWEST = ...
    NORTHEAST = ...
    SOUTHWEST = ...
    SOUTHEAST = ...


