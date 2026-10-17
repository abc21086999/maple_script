import pytest
from src.MapleMachine import Machine
from src.states.pause import Pause
from src.states.stationary import Stationary, WalkerCoolDown, WanderCoolDown
from src.states.walker import Walker
from src.states.wander import Wander
from src.states.runesolver import RuneSolver
from src.states.waiting import WalkerWaiting, WanderWaiting


class TestMapleFocus:

    @pytest.mark.parametrize("state", [Stationary, WalkerCoolDown, WanderCoolDown, Walker, Wander, RuneSolver, WalkerWaiting, WanderWaiting])
    def test_not_focus(self, test_bot, state):
        """
        測試狀態機在Stationary裡面，當楓之谷不在前景時，會不會正確切換到Pause
        """
        # 假設有按下按鍵，且不在前景
        test_bot.has_keys_pressed = True
        test_bot.maple_focus = False
        # 啟動狀態機，進入每個狀態之後測試該狀態的切換
        machine = Machine(test_bot)
        machine.current_state = state(test_bot)
        machine.current_state.enter()
        machine.switch()

        assert isinstance(machine.current_state, Pause)
        assert test_bot.has_keys_pressed == False