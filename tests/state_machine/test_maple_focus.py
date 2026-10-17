from src.MapleMachine import Machine
from src.states.pause import Pause


class TestMapleFocus:

    def test_not_focus(self, test_bot):
        test_bot.has_keys_pressed = True
        machine = Machine(test_bot)
        test_bot.maple_focus = False
        machine.run()
        assert isinstance(machine.current_state, Pause)