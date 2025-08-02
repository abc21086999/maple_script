import time
from XiaoController import XiaoController
from MapleScript import MapleScript
import PIL.Image


class DailyPrepare(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)

    def switch_to_grinding_set(self):
        self.press("f11")
        time.sleep(1)
        daily_set_image = PIL.Image.open(f"photos/daily_set.png")
        enabled_daily_set = PIL.Image.open(f"photos/enabled_daily_set.png")
        apply_button = PIL.Image.open(f"photos/daily_apply.png")
        cur_ss = self.get_full_screen_screenshot()

        if self.is_on_screen(daily_set_image, cur_ss):
            print("沒啟用")
            click_daily_set = self.calculate_distance("photos/daily_set.png")
            self.move(click_daily_set)
            self.mouse.click()
            time.sleep(0.5)
            click_apply = self.calculate_distance("photos/daily_apply.png")
            self.move(click_apply)
            self.mouse.click()
            self.press("enter")

        elif not self.is_on_screen(enabled_daily_set, cur_ss):
            print("以啟用")
            click_apply = self.calculate_distance(apply_button)
            self.move(click_apply)
            self.mouse.click()
            self.press("enter")

if __name__ == "__main__":
    with XiaoController() as controller:
        Maple = DailyPrepare(controller)
        Maple.switch_to_grinding_set()