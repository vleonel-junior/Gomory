"""Tests pour le module fraction_utils."""

import pytest
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory.fraction_utils import (
    to_fraction, floor, fractional_part, is_integer,
    format_fraction, to_fraction_list
)


class TestToFraction:
    """Tests pour la fonction to_fraction."""
    
    def test_from_int(self):
        assert to_fraction(5) == Fraction(5, 1)
        assert to_fraction(0) == Fraction(0, 1)
        assert to_fraction(-3) == Fraction(-3, 1)
    
    def test_from_fraction(self):
        f = Fraction(3, 4)
        assert to_fraction(f) == Fraction(3, 4)
    
    def test_from_string(self):
        assert to_fraction("1/2") == Fraction(1, 2)
        assert to_fraction("3/4") == Fraction(3, 4)
        assert to_fraction("-5/8") == Fraction(-5, 8)
    
    def test_from_float(self):
        result = to_fraction(0.5)
        assert result == Fraction(1, 2)


class TestFloor:
    """Tests pour la fonction floor (partie entière)."""
    
    def test_positive_integer(self):
        assert floor(Fraction(5, 1)) == 5
        assert floor(Fraction(0, 1)) == 0
    
    def test_positive_fraction(self):
        assert floor(Fraction(7, 2)) == 3  # 3.5 -> 3
        assert floor(Fraction(1, 2)) == 0  # 0.5 -> 0
        assert floor(Fraction(5, 4)) == 1  # 1.25 -> 1
    
    def test_negative_fraction(self):
        assert floor(Fraction(-3, 2)) == -2  # -1.5 -> -2
        assert floor(Fraction(-1, 2)) == -1  # -0.5 -> -1
        assert floor(Fraction(-5, 4)) == -2  # -1.25 -> -2


class TestFractionalPart:
    """Tests pour la fonction fractional_part (partie décimale)."""
    
    def test_positive_integer(self):
        assert fractional_part(Fraction(5, 1)) == Fraction(0, 1)
        assert fractional_part(Fraction(0, 1)) == Fraction(0, 1)
    
    def test_positive_fraction(self):
        assert fractional_part(Fraction(7, 2)) == Fraction(1, 2)  # 3.5 -> 0.5
        assert fractional_part(Fraction(1, 2)) == Fraction(1, 2)  # 0.5 -> 0.5
        assert fractional_part(Fraction(5, 4)) == Fraction(1, 4)  # 1.25 -> 0.25
    
    def test_negative_fraction(self):
        # Pour les nombres négatifs, {x} = x - floor(x)
        # {-1.5} = -1.5 - (-2) = 0.5
        assert fractional_part(Fraction(-3, 2)) == Fraction(1, 2)
        # {-0.5} = -0.5 - (-1) = 0.5
        assert fractional_part(Fraction(-1, 2)) == Fraction(1, 2)
        # {-1.25} = -1.25 - (-2) = 0.75
        assert fractional_part(Fraction(-5, 4)) == Fraction(3, 4)
    
    def test_fractional_part_always_nonnegative(self):
        """La partie décimale doit toujours être >= 0."""
        test_values = [
            Fraction(1, 2), Fraction(-1, 2),
            Fraction(3, 4), Fraction(-3, 4),
            Fraction(7, 8), Fraction(-7, 8),
        ]
        for val in test_values:
            fp = fractional_part(val)
            assert fp >= 0, f"fractional_part({val}) = {fp} < 0"
            assert fp < 1, f"fractional_part({val}) = {fp} >= 1"


class TestIsInteger:
    """Tests pour la fonction is_integer."""
    
    def test_integers(self):
        assert is_integer(Fraction(5, 1)) is True
        assert is_integer(Fraction(0, 1)) is True
        assert is_integer(Fraction(-3, 1)) is True
        assert is_integer(Fraction(6, 2)) is True  # = 3
        assert is_integer(Fraction(8, 4)) is True  # = 2
    
    def test_non_integers(self):
        assert is_integer(Fraction(1, 2)) is False
        assert is_integer(Fraction(3, 4)) is False
        assert is_integer(Fraction(7, 3)) is False


class TestFormatFraction:
    """Tests pour la fonction format_fraction."""
    
    def test_integer(self):
        assert format_fraction(Fraction(5, 1)) == "5"
        assert format_fraction(Fraction(-3, 1)) == "-3"
    
    def test_fraction(self):
        assert format_fraction(Fraction(3, 4)) == "3/4"
        assert format_fraction(Fraction(-1, 2)) == "-1/2"
    
    def test_with_sign(self):
        assert format_fraction(Fraction(3, 4), always_show_sign=True) == "+3/4"
        assert format_fraction(Fraction(-1, 2), always_show_sign=True) == "-1/2"


class TestToFractionList:
    """Tests pour la fonction to_fraction_list."""
    
    def test_conversion(self):
        result = to_fraction_list([1, 2, "1/2", 0.25])
        expected = [Fraction(1), Fraction(2), Fraction(1, 2), Fraction(1, 4)]
        assert result == expected
