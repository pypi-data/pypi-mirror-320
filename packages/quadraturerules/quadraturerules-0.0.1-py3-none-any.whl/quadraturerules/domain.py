"""Integral domains."""

from enum import Enum


class Domain(Enum):
    """A domain of an integral."""

    Interval = 0
    Triangle = 1
    Quadrilateral = 2
    Tetrahedron = 3
    Hexahedron = 4
