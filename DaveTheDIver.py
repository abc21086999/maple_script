from XiaoController import XiaoController
from MapleScript import MapleScript


class DaveTheDiver(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)


    def catch(self):
        for i in range(30):
            self.press_and_wait("space", 0.01)


if __name__ == "__main__":
    with XiaoController() as Xiao:
        Maple = DaveTheDiver(Xiao)
        Maple.catch()