from src.states.base import States


class Walker(States):

    def __init__(self, bot):
        super().__init__(bot)
        self.has_run = False

    def enter(self) -> None:
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
        # 跑過了就進下一個
        if self.has_run:
            if self.bot.is_loop_interval_enabled:
                self.bot.log(f"腳本執行完畢，等待下一次循環: {self.bot.route_interval_seconds} 秒")
                if self.bot.is_stationary:
                    return "WALKERCOOLDOWN"
                else:
                    return "WALKERWAITING"
            else:
                return "WANDER"
        # 執行錄製腳本模式有啟用，那就維持狀態
        if self.bot.is_route_enabled:
            return None
        # 都沒有的話就進行下一個
        return "WANDER"

    def execute(self) -> None:
        self.bot.walk_the_map()
        self.has_run = True

    def exit(self) -> None:
        self.bot.release_all()
