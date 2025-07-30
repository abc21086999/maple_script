import time
from XiaoController import XiaoController
from MapleScript import MapleScript
import PIL.Image


class DailyPrepare(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)

    def switch_to_grinding_set(self):
        self.press("f11")
        time.sleep(0.5)
        button = PIL.Image.open("photos/daily_apply.png")
        move = self.get_location_on_screen(button, self.get_full_screen_screenshot())
        self.move(move)



if __name__ == "__main__":
    with XiaoController() as controller:
        Maple = DailyPrepare(controller)
        Maple.switch_to_grinding_set()