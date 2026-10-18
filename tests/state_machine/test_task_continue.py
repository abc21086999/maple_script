import pytest
from src.MapleMachine import Machine
from src.states.pause import Pause
from src.states.stationary import Stationary, WalkerCoolDown, WanderCoolDown
from src.states.walker import Walker
from src.states.wander import Wander
from src.states.runesolver import RuneSolver
from src.states.waiting import WalkerWaiting, WanderWaiting


class TestShouldContinue:

    @pytest.mark.parametrize("state", [Stationary, WalkerCoolDown, WanderCoolDown, Walker, Wander, RuneSolver, WalkerWaiting, WanderWaiting, Pause])
    def test_machine_receive_stop_task(self, test_bot, state, mocker):
        machine = Machine(test_bot)
        machine.current_state = state(test_bot)
        machine.current_state.enter()
        original_state = machine.current_state
        exit_spy = mocker.spy(original_state, "exit")

        test_bot.keep_going = False
        machine.switch()

        assert machine.current_state is None
        exit_spy.assert_called_once()

    @pytest.mark.parametrize("state", [Stationary, WalkerCoolDown, WanderCoolDown, Walker, Wander, RuneSolver, WalkerWaiting, WanderWaiting, Pause])
    def test_state_receive_stop_task(self, test_bot, state):
        machine = Machine(test_bot)
        machine.current_state = state(test_bot)
        machine.current_state.enter()
        test_bot.keep_going = False

        assert machine.current_state.check_status() is None
