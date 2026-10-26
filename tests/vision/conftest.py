import pytest
import numpy as np
from src.utils.maple_vision import MapleVision


class MockMaple:

    pass


@pytest.fixture
def blank_minimap():
    return np.zeros((100, 200, 3), np.uint8)

@pytest.fixture
def vision():
    vision = MapleVision(MockMaple)
    return vision