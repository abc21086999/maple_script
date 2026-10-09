from src.states.base import States
from src.states.enum import StateEnum


class Wander(States):

    def __init__(self, bot):
        super().__init__(bot)
        self.has_run = False

    def enter(self) -> None:
        print(f'切換到{self.__class__.__name__}模式')

    def check_status(self) -> str | None:
        # 楓谷不在前景，進入暫停狀態
        if not self.bot.is_maple_focus():
            return StateEnum.PAUSE
        # 機器要被關閉的狀態
        if not self.bot.should_continue():
            return None
        # 有輪迴要解而且有輪迴，進入解輪狀態
        if self.bot.is_auto_solve_rune_enabled and self.bot.has_rune():
            return StateEnum.RUNESOLVER
        # 地圖上有輪迴要停下來，進入暫停狀態
        if self.bot.stop_on_rune and self.bot.has_rune():
            return StateEnum.PAUSE
        # 地圖上有人要停下來，進入暫停狀態
        if self.bot.stop_on_people and self.bot.has_other_players():
            return StateEnum.PAUSE
        # 跑過了就進下一個
        if self.has_run:
            if self.bot.is_random_wander_interval_enabled:
                self.bot.log(f"隨機跑圖結束，等待下一次循環: {self.bot.random_wander_interval_seconds} 秒")
                if self.bot.is_stationary:
                    return StateEnum.WANDERCOOLDOWN
                else:
                    return StateEnum.WANDERWAITING
            else:
                return StateEnum.STATIONARY
        # 逛逛模式有開啟，那就維持這個狀態
        if self.bot.is_random_wander_enabled:
            return None
        # 都沒有的話回到最初始狀態
        return StateEnum.STATIONARY

    def execute(self) -> None:
        self.bot.random_wander()
        self.has_run = True

    def exit(self) -> None:
        self.bot.release_all()
