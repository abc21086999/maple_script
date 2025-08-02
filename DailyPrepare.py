import time
from XiaoController import XiaoController
from MapleScript import MapleScript
import PIL.Image


class DailyPrepare(MapleScript):

    def __init__(self, controller=None):
        super().__init__(controller=controller)

    def switch_to_grinding_set(self):
        # 打開角色套組設定的界面
        self.press("f11")
        time.sleep(0.3)

        # 移動過去練功的圖案，並且點下去
        self.find_and_click_image(self.get_photo_path("daily_set.png"))
        time.sleep(0.3)

        # 移動過去套用按鈕，並且點下去
        self.find_and_click_image(self.get_photo_path("daily_apply.png"))
        time.sleep(0.3)

        # 如果有東西不一樣（出現確認按鈕）需要切換，再按下Enter
        confirm_pop_up = PIL.Image.open(self.get_photo_path("confirm_daily_pop_up.png"))
        cur_ss = self.get_full_screen_screenshot()
        if self.is_on_screen(confirm_pop_up, cur_ss):
            self.press("enter")
        time.sleep(0.3)

        # 最後不管怎麼樣，都要用Esc將界面關閉
        self.press("esc")

    def collect_union_coin(self):
        # 打開戰地聯盟的界面
        self.press("f10")
        time.sleep(0.7)

        # 按下拿硬幣的按鈕，接著用Enter關掉確認界面
        self.find_and_click_image(self.get_photo_path("get_coin.png"))
        time.sleep(0.5)
        self.press("enter")
        self.press("esc")


if __name__ == "__main__":
    with XiaoController() as controller:
        Maple = DailyPrepare(controller)
        Maple.switch_to_grinding_set()
        Maple.collect_union_coin()