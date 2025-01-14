"""Module that defines the PictorBox class."""
from decimal import Decimal

from src.pictor_lib.pictor_point import PictorPoint
from src.pictor_lib.pictor_size import PictorSize


class PictorBox:
    """Wrap a rectangle as the top-left point and the non-negative size."""

    def __init__(self, point: PictorPoint, size: PictorSize):
        self._point = point
        self._size = size

    @property
    def top(self) -> Decimal:
        """The y coordinate of top boundary."""

        return self._point.y

    @property
    def bottom(self) -> Decimal:
        """The y coordinate of bottom boundary."""

        return self._point.y + self._size.height

    @property
    def left(self) -> Decimal:
        """The x coordinate of left boundary."""

        return self._point.x

    @property
    def right(self) -> Decimal:
        """The x coordinate of right boundary."""

        return self._point.x + self._size.width

    @property
    def top_left(self) -> PictorPoint:
        """The top left point."""

        return self._point.copy()

    @property
    def top_center(self) -> PictorPoint:
        """The top center point."""

        return self._point.copy().move(self._size.width / 2, 0)

    @property
    def top_right(self) -> PictorPoint:
        """The top right point."""

        return self._point.copy().move(self._size.width, 0)

    @property
    def left_center(self) -> PictorPoint:
        """The left right point."""

        return self._point.copy().move(0, self._size.height / 2)

    @property
    def center(self) -> PictorPoint:
        """The center point."""

        return self._point.copy().move(self._size.width / 2,
                                       self._size.height / 2)

    @property
    def right_center(self) -> PictorPoint:
        """The right center point."""

        return self._point.copy().move(self._size.width, self._size.height / 2)

    @property
    def bottom_left(self) -> PictorPoint:
        """The bottom left point."""

        return self._point.copy().move(0, self._size.height)

    @property
    def bottom_center(self) -> PictorPoint:
        """The bottom center point."""

        return self._point.copy().move(self._size.width / 2, self._size.height)

    @property
    def bottom_right(self) -> PictorPoint:
        """The bottom right point."""

        return self._point.copy().move(self._size.width, self._size.height)

    @property
    def size(self) -> PictorSize:
        """The size point."""

        return self._size

    def copy(self) -> 'PictorBox':
        """Create a new box instance by copying all fields."""

        return PictorBox(point=self._point.copy(), size=self._size.copy())

    def __repr__(self) -> str:
        size_str = f'{self.size.width:0.2f}x{self.size.height:0.2f}'
        point_str = f'+{self.top_left.x:0.2f}+{self.top_right.y:0.2f}'
        return f'{size_str}{point_str}'
