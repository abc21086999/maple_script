from abc import ABC, abstractmethod
from src.MapleScript import MapleScript


POP = object()


class States(ABC):
    """
    一個狀態基類
    """

    def __init__(self, bot:MapleScript):
        self.bot = bot

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def check_status(self):
        pass

    @abstractmethod
    def exit(self):
        pass





