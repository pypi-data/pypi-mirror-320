"""Module that defines the PictorSize class."""
from decimal import Decimal

from dataclasses import dataclass
from src.pictor_lib.pictor_type import DecimalUnion


@dataclass(kw_only=True)
class PictorSize:
    """Wrap 2d size (width x height)."""

    def __init__(self, width: DecimalUnion = 0, height: DecimalUnion = 0):
        self._width = self._convert(width)
        self._height = self._convert(height)

    @property
    def width(self) -> Decimal:
        """Get the width property."""

        return self._width

    @property
    def height(self) -> Decimal:
        """Get the height property."""

        return self._height

    @property
    def raw_tuple(self) -> tuple[int, int]:
        """Convert to rounded int tuple which can be used in raw Pillow APIs."""

        return round(self.width), round(self.height)

    def copy(self) -> 'PictorSize':
        """Create a new instance by copying all fields."""

        return PictorSize(self._width, self._height)

    def set_width(self, width: DecimalUnion) -> 'PictorSize':
        """Update the width property."""

        self._width = self._convert(width)
        return self

    def set_height(self, height: DecimalUnion) -> 'PictorSize':
        """Set the height property."""

        self._height = self._convert(height)
        return self

    def scale(self, ratio: DecimalUnion) -> 'PictorSize':
        """Scale the width and height by given ratio."""

        self._width *= self._convert(ratio)
        self._height *= self._convert(ratio)
        return self

    def scale_width(self, ratio: DecimalUnion) -> 'PictorSize':
        """Scale the width by given ratio."""

        self._width *= self._convert(ratio)
        return self

    def scale_height(self, ratio: DecimalUnion) -> 'PictorSize':
        """Scale the height by given ratio."""

        self._height *= self._convert(ratio)
        return self

    def shrink_to_square(self) -> 'PictorSize':
        """Shrink the longer side to the shorter side to make a square size."""

        size = min(self.width, self.height)
        return self.set_width(size).set_height(size)

    def expand_to_square(self) -> 'PictorSize':
        """Expand the shorter side to the longer side to make a square size."""

        size = max(self.width, self.height)
        return self.set_width(size).set_height(size)

    def square_to_width(self) -> 'PictorSize':
        """Make self as square size by setting the height to width."""

        self._height = self._width
        return self

    def square_to_height(self) -> 'PictorSize':
        """Make self as square size by setting the width to height."""

        self._width = self._height
        return self

    def transpose(self) -> 'PictorSize':
        """Swap the width and height."""

        self._width, self._height = self._height, self._width
        return self

    def __add__(self, other: 'PictorSize') -> 'PictorSize':
        """Return a new size instance by adding another size object to the current object."""

        return PictorSize(self.width + other.width, self.height + other.height)

    def __sub__(self, other: 'PictorSize') -> 'PictorSize':
        """Return a new size instance by subtracting another size object from the current object."""

        return PictorSize(self.width - other.width, self.height - other.height)

    def __mul__(self, ratio: DecimalUnion) -> 'PictorSize':
        """Return a new size instance by scaling the width and height by given ratio."""

        return self.copy().scale(ratio)

    @staticmethod
    def _convert(value: DecimalUnion) -> Decimal:
        return Decimal(value)
