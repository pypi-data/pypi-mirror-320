"""Integral domains."""

from enum import Enum


class Domain(Enum):
    """A domain of an integral."""

    Tetrahedron = 0
    Triangle = 1
    Interval = 2
