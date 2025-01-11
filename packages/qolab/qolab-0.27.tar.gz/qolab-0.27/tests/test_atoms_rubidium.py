from qolab.atoms.rubidium import Rubidium
import pytest
from pytest import approx


def test_pressure_calculation():
    # liquid Rb phase
    assert Rubidium().P(333) == approx(0.0015338076093146425)
    # solid Rb phase
    assert Rubidium().P(300) == approx(6.4998452973323e-05)


def test_density_calculation():
    rb = Rubidium(line=2)  # natural abundance by default
    T = 333  # above melting point
    assert rb.N(T, "87") == approx(9.284458474584362e16)
    assert rb.N(T, "85") == approx(2.407687273125237e17)
    assert rb.N(T, "all") == approx(3.3361331205836736e17)
    assert rb.N(T, "all") == (rb.N(T, "87") + rb.N(T, "85"))
    with pytest.raises(Exception):
        assert rb.N(T, "bogus")


def test_absorption_calculation():
    rb = Rubidium(line=2)  # natural abundance by default
    T = 333  # above melting point
    assert rb.TotalAlpha(-1.9e9, T) == approx(
        37.757349154367304
    )  # affected by 85 and 87 Rb
    assert rb.TotalAlpha(1.67e9, T) == approx(
        311.8943644256937
    )  # affected by 85 Rb only
    assert rb.TotalAlpha(4.14e9, T) == approx(
        102.59365294994637
    )  # affected by 87 Rb only
