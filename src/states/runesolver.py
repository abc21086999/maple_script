from src.states.base import States, POP


class RuneSolver(States):

    def __init__(self, bot):
        super().__init__(bot)

    def enter(self) -> None:
        print(f'切換到{self.__class__.__name__}模式')
        self.bot.release_all()

    def check_status(self):
        # 楓谷不在前景，進入暫停狀態
        if not self.bot.is_maple_focus():
            return "PAUSE"
        # 機器要被關閉的狀態
        if not self.bot.should_continue():
            return None
        # 有輪迴要解而且有輪迴，那就維持狀態
        if self.bot.is_auto_solve_rune_enabled and self.bot.has_rune():
            return None
        # 沒有輪迴，那就切換到定點狀態
        return POP

    def execute(self) -> None:
        self.bot.solve_rune_encapsulation()

    def exit(self) -> None:
        self.bot.release_all()