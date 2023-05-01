from __future__ import annotations
import sys
from enum import Enum, auto
from typing import Final

RESET_COLOR: Final[str] = "\u001b[0m"

# color enum for all of the colors


class Color(Enum):
    RED = auto()
    GREEN = auto()
    YELLOW = auto()
    CYAN = auto()
    WHITE = auto()

    @staticmethod
    def get_color(color: Color) -> str:
        if color == Color.RED:
            return "\u001b[31m"
        if color == Color.GREEN:
            return "\u001b[32m"
        if color == Color.YELLOW:
            return "\u001b[33m"
        if color == Color.WHITE:
            return "\u001b[37m"
        if color == Color.CYAN:
            return "\u001b[36m"
        raise ValueError("invalid color provided")
    # i need to find a way to return the sting of the enum val without using a method


print(Color.get_color(Color.GREEN))
