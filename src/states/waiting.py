from src.states.base import States
import time


class Waiting(States):

    def __init__(self, bot, seconds = 0, next_state = None):
        super().__init__(bot)
        self.seconds = seconds
        self.endtime = None
        self.next_state = next_state

    def enter(self) -> None:
        self.bot.release_all()
        self.endtime = time.time() + self.seconds
        print(f'切換到{self.__class__.__name__}模式')

    def check_status(self) -> str | None:
        # 楓谷不在前景，進入暫停狀態
        if not self.bot.is_maple_focus():
            return "PAUSE"
        # 機器要被關閉的狀態
        if not self.bot.should_continue():
            return None
        # 有輪迴要解而且有輪迴，進入解輪狀態
        if self.bot.is_auto_solve_rune_enabled and self.bot.has_rune():
            return "RUNESOLVER"
        # 地圖上有輪迴要停下來，進入暫停狀態
        if self.bot.stop_on_rune and self.bot.has_rune():
            return "PAUSE"
        # 地圖上有人要停下來，進入暫停狀態
        if self.bot.stop_on_people and self.bot.has_other_players():
            return "PAUSE"

        # 如果現在的時間，小於應該進行到什麼時候的時間，那麼就維持狀態
        if time.time() <= self.endtime:
            return None
        # 如果有下一個狀態，那就回傳那個狀態
        if self.next_state:
            return self.next_state
        return "STATIONARY"


    def execute(self) -> None:
        self.bot.sleep(1)

    def exit(self) -> None:
        pass


class WalkerWaiting(Waiting):

    def __init__(self, bot):
        super().__init__(bot, bot.route_interval_seconds, "WANDER")


class WanderWaiting(Waiting):

    def __init__(self, bot):
        super().__init__(bot, bot.random_wander_interval_seconds, "STATIONARY")