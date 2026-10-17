import pytest


class TestBot:

    def __init__(self):
        has_keys_pressed = False

    def should_continue(self):
        return

    def is_maple_focus(self):
        return

    def release_all(self):
        return


@pytest.fixture
def test_bot():
    return TestBot()
