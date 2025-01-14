"""Test module for the class PictorBox."""

from assertpy import assert_that

from src.pictor_lib.pictor_point import PictorPoint
from src.pictor_lib.pictor_box import PictorBox
from src.pictor_lib.pictor_size import PictorSize


# pylint: disable=too-many-public-methods
class TestPictorBox:
    """Tests for the class PictorBox."""

    def test_properties(self):
        """Test for properties."""

        box = PictorBox(point=PictorPoint(67, 42), size=PictorSize(7, 5))

        # Verify box.
        assert_that(box.top).is_equal_to(42)
        assert_that(box.bottom).is_equal_to(47)
        assert_that(box.left).is_equal_to(67)
        assert_that(box.right).is_equal_to(74)
        assert_that(box.top_left).is_equal_to(PictorPoint(67, 42))
        assert_that(box.top_center).is_equal_to(PictorPoint(70.5, 42))
        assert_that(box.top_right).is_equal_to(PictorPoint(74, 42))
        assert_that(box.left_center).is_equal_to(PictorPoint(67, 44.5))
        assert_that(box.center).is_equal_to(PictorPoint(70.5, 44.5))
        assert_that(box.right_center).is_equal_to(PictorPoint(74, 44.5))
        assert_that(box.bottom_left).is_equal_to(PictorPoint(67, 47))
        assert_that(box.bottom_center).is_equal_to(PictorPoint(70.5, 47))
        assert_that(box.bottom_right).is_equal_to(PictorPoint(74, 47))
        assert_that(box.size).is_equal_to(PictorSize(7, 5))

    def test_copy(self):
        """Test for the copy method."""

        old_box = PictorBox(point=PictorPoint(67, 42), size=PictorSize(7, 5))
        new_box = old_box.copy()

        # Verify box.
        assert_that(new_box).is_not_same_as(old_box)
        assert_that(new_box.size).is_not_same_as(old_box.size)
        assert_that(new_box.size).is_equal_to(old_box.size)

    def test_to_string(self):
        """Test for converting to string."""

        box = PictorBox(point=PictorPoint(67, 42), size=PictorSize(7, 5))

        # Verify box.
        assert_that(str(box)).is_equal_to('7.00x5.00+67.00+42.00')
        assert_that(repr(box)).is_equal_to('7.00x5.00+67.00+42.00')
