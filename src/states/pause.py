from src.states.base import States, POP


class Pause(States):

    def __init__(self, bot):
        super().__init__(bot)

    def enter(self) -> None:
        print(f'切換到{self.__class__.__name__}模式')
        self.bot.release_all()

    def check_status(self):
        # 楓谷不在前景，進入暫停狀態
        if not self.bot.is_maple_focus():
            return None
        # 機器要被關閉的狀態
        if not self.bot.should_continue():
            return None
        # 地圖上有輪迴要停下來，進入暫停狀態
        if self.bot.stop_on_rune and self.bot.has_rune():
            return None
        # 地圖上有人要停下來，進入暫停狀態
        if self.bot.stop_on_people and self.bot.has_other_players():
            return None
        return POP

    def execute(self) -> None:
        self.bot.sleep(1)

    def exit(self) -> None:
        self.bot.release_all()