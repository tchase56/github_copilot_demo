import pytest
from codeComplete import add_floats

def test_add_floats_positive():
    assert add_floats(1.5, 2.5) == 4.0

def test_add_floats_negative():
    assert add_floats(-1.0, -2.0) == -3.0

def test_add_floats_zero():
    assert add_floats(0.0, 0.0) == 0.0

def test_add_floats_mixed_sign():
    assert add_floats(-1.5, 2.5) == 1.0

def test_add_floats_precision():
    result = add_floats(0.1, 0.2)
    assert pytest.approx(result, 0.0001) == 0.3
