import pytest


class TestBot:

    def __init__(self):
        self.has_keys_pressed = False
        self.keep_going = True
        self.maple_focus = True
        self.is_auto_solve_rune_enabled = False
        self.stop_on_rune = False
        self.stop_on_people = False
        self.is_stationary = False
        self.is_route_enabled = False
        self.is_random_wander_enabled = False

    def should_continue(self):
        return self.keep_going

    def is_maple_focus(self):
        return self.is_maple_focus

    def release_all(self):
        self.has_keys_pressed = False
        return


@pytest.fixture
def test_bot():
    return TestBot()
