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
        測試狀態機在不同狀態中，當楓之谷不在前景時，會不會正確切換到Pause
        """
        # 假設不在前景
        test_bot.maple_focus = False
        # 啟動狀態機，進入每個狀態之後測試該狀態的切換
        machine = Machine(test_bot)
        machine.current_state = state(test_bot)
        machine.current_state.enter()
        # 假設有按下按鍵
        test_bot.has_keys_pressed = True
        machine.switch()

        assert isinstance(machine.current_state, Pause)
        assert test_bot.has_keys_pressed == False

    @pytest.mark.parametrize("state", [Stationary, WalkerCoolDown, WanderCoolDown, Walker, Wander, RuneSolver, WalkerWaiting, WanderWaiting])
    def test_still_not_focus(self, test_bot, state):
        """
        測試狀態機在不同狀態中，當楓之谷持續不在前景時，切換到Pause後不再有新動作
        """
        # 假設不在前景
        test_bot.maple_focus = False
        # 啟動狀態機，進入每個狀態之後測試該狀態的切換
        machine = Machine(test_bot)
        machine.current_state = state(test_bot)
        machine.current_state.enter()
        # 假設有按下按鍵
        test_bot.has_keys_pressed = True
        machine.switch()
        # 假設仍然不在前景，然後再次嘗試切換狀態
        machine.switch()

        assert isinstance(machine.current_state, Pause)
        assert len(machine.stack) == 1

    @pytest.mark.parametrize("state", [Stationary, WalkerCoolDown, WanderCoolDown, Walker, Wander, RuneSolver, WalkerWaiting, WanderWaiting])
    def test_refocus(self, test_bot, state):
        """
        測試狀態機在不同狀態中，當楓之谷重新回到前景時，狀態會正確切換回來
        """
        # 假設不在前景
        test_bot.maple_focus = False
        # 啟動狀態機，進入每個狀態之後測試該狀態的切換
        machine = Machine(test_bot)
        machine.current_state = state(test_bot)
        original_state = machine.current_state
        machine.current_state.enter()
        # 假設有按下按鍵
        test_bot.has_keys_pressed = True
        machine.switch()
        # 將楓之谷切換回前景
        test_bot.maple_focus = True
        machine.switch()

        assert machine.current_state is original_state
        assert test_bot.has_keys_pressed == False
        assert len(machine.stack) == 0

    def test_not_focus_during_rune_solving(self, test_bot):
        """
        測試當狀態處在解倫時，將畫面切出楓之谷有無正常切換到暫停
        """
        # 啟動狀態機，進入Stationary
        machine = Machine(test_bot)
        machine.current_state = Stationary(test_bot)
        machine.current_state.enter()
        # 假設地圖上這時候出現輪迴
        test_bot.is_auto_solve_rune_enabled = True
        test_bot.rune_on_map = True
        # 接著轉換狀態
        machine.switch()

        assert isinstance(machine.current_state, RuneSolver)

        # 再將楓之谷切出前景
        test_bot.maple_focus = False
        machine.switch()

        assert isinstance(machine.current_state, Pause)
        assert len(machine.stack) == 2