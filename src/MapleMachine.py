from src.states.base import POP
from src.states.stationary import Stationary, WalkerCoolDown, WanderCoolDown
from src.states.pause import Pause
from src.states.walker import Walker
from src.states.wander import Wander
from src.states.runesolver import RuneSolver
from src.states.waiting import Waiting, WalkerWaiting, WanderWaiting
from src.MapleScript import MapleScript


class Machine:

    state_mapping = {
        "STATIONARY" : Stationary,
        "WALKER": Walker,
        "WANDER": Wander,
        "RUNESOLVER": RuneSolver,
        "PAUSE": Pause,
        "WALKERCOOLDOWN": WalkerCoolDown,
        "WANDERCOOLDOWN": WanderCoolDown,
        "WAITING": Waiting,
        "WALKERWAITING": WalkerWaiting,
        "WANDERWAITING": WanderWaiting,
    }

    def __init__(self, bot: MapleScript):
        self.bot = bot
        self.current_state = None
        self.stack = []

    def switch(self) -> bool:
        """
        檢查狀態須不需要切換
        :return: None
        """
        # 偵測到練功要停止
        if not self.bot.should_continue():
            if self.current_state is not None:
                self.current_state.exit()
            return False

        # 切換狀態
        check_result = self.current_state.check_status()

        # 維持現狀
        if check_result is None:
            return False

        # 從暫停狀態恢復上一個狀態
        elif check_result is POP:
            if self.stack:
                self.current_state.exit()
                self.current_state = self.stack.pop()
                return True
            else:
                print("狀態機內Stack為空")

        # 進入暫停狀態
        elif check_result in {"PAUSE", "RUNESOLVER"}:
            last_state = self.current_state
            self.stack.append(last_state)
            self.current_state.exit()
            self.current_state = self.state_mapping.get(check_result)(self.bot)
            self.current_state.enter()
            return True

        # 進入其他狀態
        elif check_result and check_result in self.state_mapping:
            self.current_state.exit()
            self.current_state = self.state_mapping.get(check_result)(self.bot)
            self.current_state.enter()
            return True
        return False

    def run(self):
        """
        啟動狀態機
        :return: None
        """
        # 初始化機器的第一個工作：定點練功
        self.current_state = Stationary(self.bot)
        self.current_state.enter()

        # 機器沒收到停止動作的訊號就繼續
        while self.bot.should_continue():
            status_change = self.switch()
            if not status_change and self.bot.should_continue():
                self.current_state.execute()
