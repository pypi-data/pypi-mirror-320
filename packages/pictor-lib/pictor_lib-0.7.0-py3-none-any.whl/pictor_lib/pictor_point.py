"""Module that defines the PictorPoint class."""
from decimal import Decimal

from dataclasses import dataclass
from src.pictor_lib.pictor_type import DecimalUnion


@dataclass(kw_only=True)
class PictorPoint:
    """Wrap 2d point (x, y)."""

    def __init__(self, x: DecimalUnion = 0, y: DecimalUnion = 0):
        self._x = self._convert(x)
        self._y = self._convert(y)

    @property
    def x(self) -> Decimal:
        """Get the x property."""

        return self._x

    @property
    def y(self) -> Decimal:
        """Get the y property."""

        return self._y

    @property
    def raw_tuple(self) -> tuple[int, int]:
        """Convert to rounded int tuple which can be used in raw Pillow APIs."""

        return round(self.x), round(self.y)

    def copy(self) -> 'PictorPoint':
        """Create a new instance by copying all fields."""

        return PictorPoint(self._x, self._y)

    def set_x(self, x: DecimalUnion) -> 'PictorPoint':
        """Update the x property."""

        self._x = self._convert(x)
        return self

    def set_y(self, y: DecimalUnion) -> 'PictorPoint':
        """Set the y property."""

        self._y = self._convert(y)
        return self

    def move(self, dx: DecimalUnion, dy: DecimalUnion) -> 'PictorPoint':
        """Move the point by given (dx, dy) offset."""

        self._x += dx
        self._y += dy
        return self

    @staticmethod
    def _convert(value: DecimalUnion) -> Decimal:
        return Decimal(value)


PictorPoint.ORIGIN = PictorPoint(0, 0)
